import json
import os
import sys
import subprocess
import threading
import datetime
import glob
import shutil

from flask import Flask, render_template, request, jsonify, send_from_directory
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

from config import (
    FIREWORKS_API_KEY, FIREWORKS_BASE_URL, FIREWORKS_MODEL_CHEAP, FIREWORKS_MODEL_QUALITY,
    DATA_DIR, OUTPUT_DIR, LOGS_DIR, APP_NAME, APP_LINK,
    REDDIT_SUBREDDITS, VIDEO_WIDTH, VIDEO_HEIGHT
)

fw = OpenAI(api_key=FIREWORKS_API_KEY, base_url=FIREWORKS_BASE_URL)
app = Flask(__name__, template_folder="templates_web", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

def fw_call(model, messages, max_tokens=4000, temperature=0.7):
    if max_tokens > 4096:
        resp = fw.chat.completions.create(model=model, messages=messages, max_tokens=max_tokens, temperature=temperature, stream=True)
        chunks = []
        try:
            for chunk in resp:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        chunks.append(delta.content)
        except: pass
        return "".join(chunks)
    else:
        resp = fw.chat.completions.create(model=model, messages=messages, max_tokens=max_tokens, temperature=temperature)
        return resp.choices[0].message.content or ""

for d in [DATA_DIR, OUTPUT_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

tasks = {}

def _run_py(script_name):
    path = os.path.join(SCRIPTS_DIR, script_name)
    r = subprocess.run([sys.executable, path], capture_output=True, text=True, cwd=BASE_DIR, timeout=600)
    return {"ok": r.returncode == 0, "stdout": r.stdout[-2000:], "stderr": r.stderr[-500:]}

def _bg(task_id, fn, *a):
    tasks[task_id] = {"status": "running", "started": datetime.datetime.now().isoformat()}
    try:
        res = fn(*a)
        tasks[task_id].update({"status": "done", "finished": datetime.datetime.now().isoformat(), "result": res})
    except Exception as e:
        tasks[task_id].update({"status": "error", "error": str(e)})

def _tid(prefix):
    return f"{prefix}_{datetime.datetime.now().strftime('%H%M%S')}"

def _start(prefix, fn):
    tid = _tid(prefix)
    threading.Thread(target=_bg, args=(tid, fn), daemon=True).start()
    return tid

@app.route("/")
def index():
    # Use v2 dashboard if available, fallback to original
    try:
        return render_template("dashboard_v2.html")
    except:
        return render_template("dashboard.html")

@app.route("/v1")
def dashboard_v1():
    return render_template("dashboard.html")

@app.route("/v2")
def dashboard_v2():
    return render_template("dashboard_v2.html")

@app.route("/ru")
def dashboard_ru():
    return render_template("dashboard_ru.html")

@app.route("/v3")
def dashboard_v3():
    return render_template("dashboard_ru.html")

@app.route("/api/status")
def api_status():
    s = {"app_name": APP_NAME, "scenarios": 0, "videos": 0, "posted": 0,
         "reddit_answers": 0, "comment_replies": 0, "tasks": tasks}
    p = os.path.join(DATA_DIR, "scenarios_latest.json")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f: s["scenarios"] = len(json.load(f))
    vd = os.path.join(OUTPUT_DIR, "videos")
    if os.path.exists(vd): s["videos"] = len(glob.glob(os.path.join(vd, "*.mp4")))
    for key, file, field in [("posted","posted_videos.json","posted"),("reddit_answers","reddit_answered.json","answered_ids"),("comment_replies","comments_replied.json","replied")]:
        fp = os.path.join(DATA_DIR, file)
        if os.path.exists(fp):
            with open(fp, "r", encoding="utf-8") as f: s[key] = len(json.load(f).get(field, []))
    return jsonify(s)

@app.route("/api/task/<tid>")
def api_task(tid):
    return jsonify(tasks.get(tid, {"status": "not_found"}))

@app.route("/api/run/<action>", methods=["POST"])
def api_run(action):
    mapping = {
        "scenarios": lambda: _run_py("01_generate_scenarios.py"),
        "frames": lambda: _run_py("02_generate_frames.py"),
        "videos": lambda: _run_py("03_assemble_videos.py"),
        "audio": lambda: _run_py("03_assemble_videos.py"),
        "reddit": lambda: _run_py("05_reddit_responder.py"),
        "analytics": lambda: _run_py("07_analytics_report.py"),
    }
    if action == "pipeline":
        def pipe():
            r1 = _run_py("01_generate_scenarios.py")
            r2 = _run_py("02_generate_frames.py")
            r3 = _run_py("03_assemble_videos.py")
            return {"scenarios": r1, "frames": r2, "videos": r3}
        tid = _start("pipeline", pipe)
    elif action in mapping:
        tid = _start(action, mapping[action])
    else:
        return jsonify({"error": f"Unknown action: {action}"}), 400
    return jsonify({"task_id": tid, "message": f"Running {action}..."})

@app.route("/api/scenarios")
def api_scenarios():
    p = os.path.join(DATA_DIR, "scenarios_latest.json")
    if not os.path.exists(p): return jsonify([])
    with open(p, "r", encoding="utf-8") as f: return jsonify(json.load(f))

@app.route("/api/scenarios", methods=["POST"])
def api_save_scenarios():
    data = request.json
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    for name in [f"scenarios_{ts}.json", "scenarios_latest.json"]:
        with open(os.path.join(DATA_DIR, name), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True, "count": len(data)})

@app.route("/api/scenarios/generate_one", methods=["POST"])
def api_gen_one():
    t = request.json.get("type", "random")
    prompt = f"""Generate ONE TikTok video scenario (15-30 sec) for "{APP_NAME}" (Arabic+English learning app, includes dialects).
Type: {t}
Output ONLY JSON, no markdown:
{{"id":0,"type":"type_name","hook_en":"English hook","hook_ar":"Arabic hook","items":[{{"en":"English","ar":"Arabic","pronunciation":"romanized"}}],"cta_en":"CTA mentioning {APP_NAME}","cta_ar":"Arabic CTA","hashtags":["#learnarabic"]}}
3-5 items, Arabic script AND pronunciation, make it FUN."""
    try:
        r = fw_call(FIREWORKS_MODEL_QUALITY, [{"role":"user","content":prompt}], max_tokens=600, temperature=0.9)
        js, je = r.find("{"), r.rfind("}")+1
        if js == -1: return jsonify({"error":"No JSON","raw":r}), 500
        sc = json.loads(r[js:je])
        sc["id"] = int(datetime.datetime.now().timestamp())
        return jsonify(sc)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/videos")
def api_videos():
    vd = os.path.join(OUTPUT_DIR, "videos")
    if not os.path.exists(vd): return jsonify([])
    return jsonify([{"filename": os.path.basename(f),
                     "size_kb": round(os.path.getsize(f)/1024),
                     "modified": datetime.datetime.fromtimestamp(os.path.getmtime(f)).isoformat()}
                    for f in sorted(glob.glob(os.path.join(vd, "*.mp4")))])

@app.route("/api/videos/<fn>")
def api_video_dl(fn):
    return send_from_directory(os.path.join(OUTPUT_DIR, "videos"), fn)

@app.route("/api/logs")
def api_logs():
    logs = {}
    for lf in glob.glob(os.path.join(LOGS_DIR, "*.log")):
        name = os.path.basename(lf).replace(".log","")
        try:
            with open(lf,"r",encoding="utf-8") as f: logs[name] = "".join(f.readlines()[-80:])
        except: logs[name] = "read error"
    return jsonify(logs)

@app.route("/api/reports/latest")
def api_report():
    p = os.path.join(DATA_DIR, "report_latest.md")
    if not os.path.exists(p): return jsonify({"content":"No report yet. Run analytics first."})
    with open(p,"r",encoding="utf-8") as f: return jsonify({"content":f.read()})

@app.route("/api/comment_reply", methods=["POST"])
def api_comment():
    c = request.json.get("comment","")
    ctx = request.json.get("post","")
    sys_p = f'You are a friendly community manager for "{APP_NAME}". Respond in the SAME LANGUAGE. 1-2 sentences. Mention: Arabic dialects, English, flashcards if relevant.'
    try:
        r = fw_call(FIREWORKS_MODEL_CHEAP, [{"role":"system","content":sys_p},{"role":"user","content":f"Post:{ctx}\nComment:{c}"}], max_tokens=150, temperature=0.7)
        return jsonify({"reply": r.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/quora_answer", methods=["POST"])
def api_quora():
    q = request.json.get("question","")
    d = request.json.get("detail","")
    sys_p = f'Bilingual Arabic+English expert. Include Arabic script+pronunciation. IF about languages, add: "Check out {APP_NAME} — {APP_LINK}". Otherwise answer normally.'
    try:
        ctx = f"Question:{q}"
        if d: ctx += f"\nDetails:{d}"
        r = fw_call(FIREWORKS_MODEL_CHEAP, [{"role":"system","content":sys_p},{"role":"user","content":ctx}], max_tokens=800, temperature=0.7)
        return jsonify({"answer": r})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/config")
def api_config():
    import importlib
    from modules.scenario_validator import ScenarioValidator

    return jsonify({
        "app_name": APP_NAME,
        "app_link": APP_LINK,
        "subreddits": REDDIT_SUBREDDITS,
        "video_w": VIDEO_WIDTH,
        "video_h": VIDEO_HEIGHT,
        "features": {
            "tts_enabled": True,
            "background_music_enabled": True,
            "video_effects_enabled": True
        }
    })

@app.route("/api/health")
def api_health():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "version": "2.0.0",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route("/api/storage")
def api_storage():
    """Get storage information"""
    def get_size(path):
        total = 0
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total += os.path.getsize(filepath)
        return round(total / (1024 * 1024), 2)

    return jsonify({
        "output_mb": get_size(os.path.join(OUTPUT_DIR, "videos")),
        "data_mb": get_size(DATA_DIR),
        "logs_mb": get_size(LOGS_DIR),
        "total_mb": get_size(OUTPUT_DIR) + get_size(DATA_DIR) + get_size(LOGS_DIR)
    })

@app.route("/api/system/info")
def api_system_info():
    """Get system information"""
    try:
        import psutil
        return jsonify({
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent
        })
    except:
        return jsonify({"status": "info unavailable"})

if __name__ == "__main__":
    print(f"\n  {APP_NAME} — Dashboard: http://localhost:5000\n")
    app.run(debug=True, port=5000)
