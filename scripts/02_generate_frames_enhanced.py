import json
import os
import sys
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import (
    DATA_DIR, OUTPUT_DIR, VIDEO_WIDTH, VIDEO_HEIGHT,
    BG_COLOR_DARK, BG_COLOR_ACCENT, TEXT_COLOR_WHITE, TEXT_COLOR_GOLD, TEXT_COLOR_GREEN,
    SECONDS_PER_FRAME, LOGS_DIR, APP_NAME
)
from modules.scenario_validator import ScenarioValidator

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "frame_gen.log")),
        logging.StreamHandler()
    ]
)


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load font with fallback"""
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
    except Exception as e:
        logger.warning(f"Could not load font {size}px: {e}")
    return ImageFont.load_default()


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def draw_gradient_bg(draw: ImageDraw.ImageDraw, width: int, height: int,
                      color_top: str, color_bottom: str):
    """Draw gradient background"""
    r1, g1, b1 = hex_to_rgb(color_top)
    r2, g2, b2 = hex_to_rgb(color_bottom)
    for y in range(height):
        ratio = y / height
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_centered_text(draw: ImageDraw.ImageDraw, text: str, y: int,
                        font: ImageFont.FreeTypeFont, fill: tuple):
    """Draw centered text"""
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (VIDEO_WIDTH - tw) // 2
        draw.text((x, y), text, font=font, fill=fill)
    except Exception as e:
        logger.error(f"Error drawing text '{text[:30]}...': {e}")


def make_hook_frame(scenario: dict, filename: str) -> bool:
    """Create hook frame"""
    try:
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT))
        draw = ImageDraw.Draw(img)
        draw_gradient_bg(draw, VIDEO_WIDTH, VIDEO_HEIGHT, "#0a0a1a", BG_COLOR_DARK)

        logo_font = get_font(48, bold=True)
        hook_font = get_font(64, bold=True)
        sub_font = get_font(40)

        draw_centered_text(draw, APP_NAME, 120, logo_font, hex_to_rgb(TEXT_COLOR_GOLD))
        draw_centered_text(draw, scenario.get("hook_en", ""), 400, hook_font, hex_to_rgb(TEXT_COLOR_WHITE))
        draw_centered_text(draw, scenario.get("hook_ar", ""), 520, sub_font, hex_to_rgb(TEXT_COLOR_GREEN))

        arrow_font = get_font(80)
        draw_centered_text(draw, "▼", 700, arrow_font, hex_to_rgb(TEXT_COLOR_GOLD))

        img.save(filename)
        logger.debug(f"Hook frame created: {filename}")
        return True
    except Exception as e:
        logger.error(f"Error creating hook frame: {e}")
        return False


def make_item_frame(item: dict, index: int, total: int, scenario_type: str, filename: str) -> bool:
    """Create item frame"""
    try:
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT))
        draw = ImageDraw.Draw(img)
        draw_gradient_bg(draw, VIDEO_WIDTH, VIDEO_HEIGHT, BG_COLOR_DARK, BG_COLOR_ACCENT)

        num_font = get_font(36, bold=True)
        en_font = get_font(56, bold=True)
        ar_font = get_font(52)
        pron_font = get_font(36)

        draw_centered_text(draw, f"{index + 1}/{total}", 100, num_font, hex_to_rgb(TEXT_COLOR_GOLD))
        draw_centered_text(draw, item["en"], 350, en_font, hex_to_rgb(TEXT_COLOR_WHITE))
        draw_centered_text(draw, item["ar"], 500, ar_font, hex_to_rgb(TEXT_COLOR_GREEN))

        if "pronunciation" in item and item["pronunciation"]:
            draw_centered_text(draw, f"[{item['pronunciation']}]", 650, pron_font, hex_to_rgb("#aaaaaa"))

        progress_y = 1600
        bar_width = int((VIDEO_WIDTH - 200) * ((index + 1) / total))
        draw.rounded_rectangle([100, progress_y, 100 + bar_width, progress_y + 12],
                               radius=6, fill=hex_to_rgb(TEXT_COLOR_GOLD))
        draw.rounded_rectangle([100, progress_y, VIDEO_WIDTH - 100, progress_y + 12],
                               radius=6, outline=hex_to_rgb("#333333"))

        img.save(filename)
        logger.debug(f"Item frame created: {filename}")
        return True
    except Exception as e:
        logger.error(f"Error creating item frame {index}: {e}")
        return False


def make_cta_frame(scenario: dict, filename: str) -> bool:
    """Create call-to-action frame"""
    try:
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT))
        draw = ImageDraw.Draw(img)
        draw_gradient_bg(draw, VIDEO_WIDTH, VIDEO_HEIGHT, "#0a0a1a", "#1a0a2e")

        cta_font = get_font(52, bold=True)
        app_font = get_font(72, bold=True)
        link_font = get_font(32)

        draw_centered_text(draw, scenario["cta_en"], 400, cta_font, hex_to_rgb(TEXT_COLOR_WHITE))
        draw_centered_text(draw, scenario["cta_ar"], 550, cta_font, hex_to_rgb(TEXT_COLOR_GREEN))

        draw.rounded_rectangle(
            [VIDEO_WIDTH//2 - 300, 750, VIDEO_WIDTH//2 + 300, 900],
            radius=20, fill=hex_to_rgb(TEXT_COLOR_GOLD)
        )
        draw_centered_text(draw, APP_NAME, 790, app_font, hex_to_rgb("#000000"))
        draw_centered_text(draw, "FREE DOWNLOAD", 1000, link_font, hex_to_rgb(TEXT_COLOR_WHITE))

        img.save(filename)
        logger.debug(f"CTA frame created: {filename}")
        return True
    except Exception as e:
        logger.error(f"Error creating CTA frame: {e}")
        return False


def generate_frames():
    """Main frame generation function"""
    scenarios_path = os.path.join(DATA_DIR, "scenarios_latest.json")
    if not os.path.exists(scenarios_path):
        logger.error("No scenarios found. Run 01_generate_scenarios.py first.")
        return

    with open(scenarios_path, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    scenarios = [s for s in scenarios if isinstance(s, dict) and "id" in s and "items" in s]

    valid_scenarios, invalid = ScenarioValidator.validate_scenarios(scenarios)

    if invalid:
        logger.warning(f"Found {len(invalid)} invalid scenarios, filtering them out")

    if not valid_scenarios:
        logger.error("No valid scenarios found. Check your scenarios_latest.json")
        return

    frames_dir = os.path.join(OUTPUT_DIR, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    manifest = []
    frame_stats = {"success": 0, "failed": 0}

    logger.info(f"Generating frames for {len(valid_scenarios)} scenarios...")

    for scenario in valid_scenarios:
        sid = scenario["id"]
        scenario_frames_dir = os.path.join(frames_dir, f"scenario_{sid:03d}")
        os.makedirs(scenario_frames_dir, exist_ok=True)

        frame_list = []

        hook_path = os.path.join(scenario_frames_dir, "frame_00_hook.png")
        if make_hook_frame(scenario, hook_path):
            frame_list.append(hook_path)
        else:
            frame_stats["failed"] += 1
            continue

        for i, item in enumerate(scenario["items"]):
            item_path = os.path.join(scenario_frames_dir, f"frame_{i+1:02d}_item.png")
            if make_item_frame(item, i, len(scenario["items"]), scenario["type"], item_path):
                frame_list.append(item_path)
            else:
                logger.warning(f"Failed to create item frame {i} for scenario {sid}")

        cta_path = os.path.join(scenario_frames_dir, f"frame_{len(scenario['items'])+1:02d}_cta.png")
        if make_cta_frame(scenario, cta_path):
            frame_list.append(cta_path)
        else:
            logger.warning(f"Failed to create CTA frame for scenario {sid}")

        if frame_list:
            manifest.append({
                "id": sid,
                "type": scenario["type"],
                "frames": frame_list,
                "hashtags": scenario.get("hashtags", []),
                "hook_en": scenario["hook_en"],
                "cta_en": scenario["cta_en"]
            })
            frame_stats["success"] += 1
            logger.info(f"✓ Scenario {sid}: {len(frame_list)} frames")

    manifest_path = os.path.join(DATA_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    logger.info("=" * 50)
    logger.info(f"Frame Generation Complete:")
    logger.info(f"✓ Success: {frame_stats['success']}")
    logger.info(f"✗ Failed: {frame_stats['failed']}")
    logger.info(f"Manifest: {manifest_path}")
    logger.info("=" * 50)

    print(f"\n✓ Generated frames for {len(manifest)} scenarios\n")


if __name__ == "__main__":
    generate_frames()
