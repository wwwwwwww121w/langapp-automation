import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'core'))
from config import (
    DATA_DIR, OUTPUT_DIR, VIDEO_WIDTH, VIDEO_HEIGHT,
    BG_COLOR_DARK, BG_COLOR_ACCENT, TEXT_COLOR_WHITE, TEXT_COLOR_GOLD, TEXT_COLOR_GREEN,
    SECONDS_PER_FRAME, APP_NAME
)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

def get_font(size, bold=False):
    try:
        paths = [
            "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
        for p in paths:
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    except:
        pass
    return ImageFont.load_default()

def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def draw_gradient_bg(draw, width, height, color_top, color_bottom):
    r1, g1, b1 = hex_to_rgb(color_top)
    r2, g2, b2 = hex_to_rgb(color_bottom)
    for y in range(height):
        ratio = y / height
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

def draw_centered_text(draw, text, y, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (VIDEO_WIDTH - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)

def make_hook_frame(scenario, filename):
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT))
    draw = ImageDraw.Draw(img)
    draw_gradient_bg(draw, VIDEO_WIDTH, VIDEO_HEIGHT, "#0a0a1a", BG_COLOR_DARK)

    # High-quality fonts scaled for 1440x2560 resolution
    logo_font = get_font(68, bold=True)
    hook_font = get_font(92, bold=True)
    sub_font = get_font(56)

    draw_centered_text(draw, APP_NAME, 160, logo_font, hex_to_rgb(TEXT_COLOR_GOLD))

    draw_centered_text(draw, scenario.get("hook_en", ""), 560, hook_font, hex_to_rgb(TEXT_COLOR_WHITE))
    draw_centered_text(draw, scenario.get("hook_ar", ""), 740, sub_font, hex_to_rgb(TEXT_COLOR_GREEN))

    arrow_font = get_font(112)
    draw_centered_text(draw, "▼", 980, arrow_font, hex_to_rgb(TEXT_COLOR_GOLD))

    img.save(filename)

def make_item_frame(item, index, total, scenario_type, filename):
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT))
    draw = ImageDraw.Draw(img)
    draw_gradient_bg(draw, VIDEO_WIDTH, VIDEO_HEIGHT, BG_COLOR_DARK, BG_COLOR_ACCENT)

    # High-quality fonts scaled for 1440x2560 resolution
    num_font = get_font(50, bold=True)
    en_font = get_font(80, bold=True)
    ar_font = get_font(74)
    pron_font = get_font(50)

    draw_centered_text(draw, f"{index + 1}/{total}", 140, num_font, hex_to_rgb(TEXT_COLOR_GOLD))

    draw_centered_text(draw, item["en"], 490, en_font, hex_to_rgb(TEXT_COLOR_WHITE))
    draw_centered_text(draw, item["ar"], 700, ar_font, hex_to_rgb(TEXT_COLOR_GREEN))

    if "pronunciation" in item and item["pronunciation"]:
        draw_centered_text(draw, f"[{item['pronunciation']}]", 910, pron_font, hex_to_rgb("#aaaaaa"))

    # Progress bar - scaled for new resolution
    progress_y = 2240
    bar_width = int((VIDEO_WIDTH - 280) * ((index + 1) / total))
    draw.rounded_rectangle([140, progress_y, 140 + bar_width, progress_y + 16],
                           radius=8, fill=hex_to_rgb(TEXT_COLOR_GOLD))
    draw.rounded_rectangle([140, progress_y, VIDEO_WIDTH - 140, progress_y + 16],
                           radius=8, outline=hex_to_rgb("#333333"))

    img.save(filename)

def make_cta_frame(scenario, filename):
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT))
    draw = ImageDraw.Draw(img)
    draw_gradient_bg(draw, VIDEO_WIDTH, VIDEO_HEIGHT, "#0a0a1a", "#1a0a2e")

    # High-quality fonts scaled for 1440x2560 resolution
    cta_font = get_font(74, bold=True)
    app_font = get_font(104, bold=True)
    link_font = get_font(46)

    draw_centered_text(draw, scenario["cta_en"], 560, cta_font, hex_to_rgb(TEXT_COLOR_WHITE))
    draw_centered_text(draw, scenario["cta_ar"], 770, cta_font, hex_to_rgb(TEXT_COLOR_GREEN))

    # Scaled button for new resolution
    draw.rounded_rectangle(
        [VIDEO_WIDTH//2 - 420, 1050, VIDEO_WIDTH//2 + 420, 1260],
        radius=28, fill=hex_to_rgb(TEXT_COLOR_GOLD)
    )
    draw_centered_text(draw, APP_NAME, 1110, app_font, hex_to_rgb("#000000"))

    draw_centered_text(draw, "FREE DOWNLOAD", 1400, link_font, hex_to_rgb(TEXT_COLOR_WHITE))

    img.save(filename)

def generate_frames():
    scenarios_path = os.path.join(DATA_DIR, "scenarios_latest.json")
    if not os.path.exists(scenarios_path):
        print("No scenarios found. Run 01_generate_scenarios.py first.")
        return
    
    with open(scenarios_path, "r", encoding="utf-8") as f:
        scenarios = json.load(f)
    
    scenarios = [s for s in scenarios if isinstance(s, dict) and "id" in s and "items" in s]
    
    if not scenarios:
        print("No valid scenarios found. Run 01_generate_scenarios.py first.")
        return
    
    frames_dir = os.path.join(OUTPUT_DIR, "frames")
    
    manifest = []
    
    for scenario in scenarios:
        sid = scenario["id"]
        scenario_frames_dir = os.path.join(frames_dir, f"scenario_{sid:03d}")
        os.makedirs(scenario_frames_dir, exist_ok=True)
        
        frame_list = []
        
        hook_path = os.path.join(scenario_frames_dir, "frame_00_hook.png")
        make_hook_frame(scenario, hook_path)
        frame_list.append(hook_path)
        
        for i, item in enumerate(scenario["items"]):
            item_path = os.path.join(scenario_frames_dir, f"frame_{i+1:02d}_item.png")
            make_item_frame(item, i, len(scenario["items"]), scenario["type"], item_path)
            frame_list.append(item_path)
        
        cta_path = os.path.join(scenario_frames_dir, f"frame_{len(scenario['items'])+1:02d}_cta.png")
        make_cta_frame(scenario, cta_path)
        frame_list.append(cta_path)
        
        manifest.append({
            "id": sid,
            "type": scenario["type"],
            "frames": frame_list,
            "hashtags": scenario.get("hashtags", []),
            "hook_en": scenario["hook_en"],
            "cta_en": scenario["cta_en"]
        })
    
    manifest_path = os.path.join(DATA_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print(f"Generated frames for {len(scenarios)} scenarios")
    print(f"Manifest saved to {manifest_path}")

if __name__ == "__main__":
    generate_frames()
