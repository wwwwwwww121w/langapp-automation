#!/usr/bin/env python3
"""
Unified video generation pipeline with logging, error handling, and progress tracking
"""

import os
import sys
import json
import time
import logging
import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from config import DATA_DIR, OUTPUT_DIR, LOGS_DIR, ENABLE_TTS
from modules.audio_generator import AudioGenerator
from modules.scenario_validator import ScenarioValidator

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "pipeline.log")),
        logging.StreamHandler()
    ]
)


class Pipeline:
    def __init__(self, enable_audio: bool = ENABLE_TTS):
        self.enable_audio = enable_audio
        self.results = {
            "start_time": datetime.datetime.now().isoformat(),
            "steps": {}
        }
        logger.info("Pipeline initialized")

    def log_step(self, step_name: str, status: str, details: dict = None):
        """Log pipeline step"""
        self.results["steps"][step_name] = {
            "status": status,
            "timestamp": datetime.datetime.now().isoformat(),
            "details": details or {}
        }
        logger.info(f"{'='*50}")
        logger.info(f"Step: {step_name}")
        logger.info(f"Status: {status}")
        if details:
            for k, v in details.items():
                logger.info(f"  {k}: {v}")
        logger.info(f"{'='*50}")

    def step_generate_scenarios(self):
        """Step 1: Generate scenarios"""
        logger.info("\n🎬 STEP 1: Generate Scenarios")
        try:
            from scripts.import_module_01_generate_scenarios_enhanced import generate_scenarios
            scenarios = generate_scenarios()

            if scenarios:
                self.log_step("generate_scenarios", "SUCCESS", {
                    "count": len(scenarios),
                    "file": os.path.join(DATA_DIR, "scenarios_latest.json")
                })
                return True
            else:
                self.log_step("generate_scenarios", "FAILED", {"error": "No scenarios generated"})
                return False

        except ImportError:
            import subprocess
            result = subprocess.run(
                [sys.executable, os.path.join(Path(__file__).parent, "01_generate_scenarios_enhanced.py")],
                capture_output=True, text=True, timeout=600
            )
            if result.returncode == 0:
                with open(os.path.join(DATA_DIR, "scenarios_latest.json")) as f:
                    scenarios = json.load(f)
                self.log_step("generate_scenarios", "SUCCESS", {"count": len(scenarios)})
                return True
            else:
                self.log_step("generate_scenarios", "FAILED", {"stderr": result.stderr[-500:]})
                return False
        except Exception as e:
            logger.error(f"Error in step_generate_scenarios: {e}", exc_info=True)
            self.log_step("generate_scenarios", "ERROR", {"error": str(e)})
            return False

    def step_validate_scenarios(self):
        """Step 2: Validate scenarios"""
        logger.info("\n✓ STEP 2: Validate Scenarios")
        try:
            scenarios_path = os.path.join(DATA_DIR, "scenarios_latest.json")
            if not os.path.exists(scenarios_path):
                self.log_step("validate_scenarios", "SKIPPED", {"reason": "No scenarios file"})
                return False

            with open(scenarios_path) as f:
                scenarios = json.load(f)

            valid, invalid = ScenarioValidator.validate_scenarios(scenarios)
            logger.info(f"Validation: {len(valid)} valid, {len(invalid)} invalid")

            if invalid:
                logger.warning("Fixing invalid scenarios...")
                fixed_count = 0
                for item in invalid:
                    fixed = ScenarioValidator.fix_scenario(item["scenario"])
                    is_valid, _ = ScenarioValidator.validate_scenario(fixed)
                    if is_valid:
                        valid.append(fixed)
                        fixed_count += 1

                logger.info(f"Fixed {fixed_count}/{len(invalid)} scenarios")

            with open(scenarios_path, "w") as f:
                json.dump(valid, f, ensure_ascii=False, indent=2)

            self.log_step("validate_scenarios", "SUCCESS", {
                "valid": len(valid),
                "invalid_fixed": fixed_count if invalid else 0
            })
            return True

        except Exception as e:
            logger.error(f"Error in step_validate_scenarios: {e}", exc_info=True)
            self.log_step("validate_scenarios", "ERROR", {"error": str(e)})
            return False

    def step_generate_audio(self):
        """Step 3: Generate audio (optional)"""
        if not self.enable_audio:
            logger.info("\n🔇 STEP 3: Audio Generation (DISABLED)")
            self.log_step("generate_audio", "SKIPPED", {"reason": "TTS disabled in config"})
            return True

        logger.info("\n🔊 STEP 3: Generate Audio")
        try:
            audio_gen = AudioGenerator()
            scenarios_path = os.path.join(DATA_DIR, "scenarios_latest.json")

            with open(scenarios_path) as f:
                scenarios = json.load(f)

            os.makedirs(os.path.join(OUTPUT_DIR, "audio"), exist_ok=True)

            for scenario in scenarios[:3]:
                audio_info = audio_gen.create_scenario_audio(scenario)
                logger.debug(f"Scenario {scenario.get('id')}: {audio_info}")

            self.log_step("generate_audio", "SUCCESS", {
                "generator_initialized": True,
                "scenarios_processed": min(3, len(scenarios))
            })
            return True

        except Exception as e:
            logger.warning(f"Audio generation skipped: {e}")
            self.log_step("generate_audio", "SKIPPED", {"error": str(e)})
            return True

    def step_generate_frames(self):
        """Step 4: Generate frames"""
        logger.info("\n🖼️ STEP 4: Generate Frames")
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, os.path.join(Path(__file__).parent, "02_generate_frames_enhanced.py")],
                capture_output=True, text=True, timeout=600
            )

            if result.returncode == 0:
                manifest_path = os.path.join(DATA_DIR, "manifest.json")
                with open(manifest_path) as f:
                    manifest = json.load(f)

                self.log_step("generate_frames", "SUCCESS", {"frames_generated": len(manifest)})
                return True
            else:
                self.log_step("generate_frames", "FAILED", {"stderr": result.stderr[-500:]})
                return False

        except Exception as e:
            logger.error(f"Error in step_generate_frames: {e}", exc_info=True)
            self.log_step("generate_frames", "ERROR", {"error": str(e)})
            return False

    def step_assemble_videos(self):
        """Step 5: Assemble videos"""
        logger.info("\n🎞️ STEP 5: Assemble Videos")
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, os.path.join(Path(__file__).parent, "03_assemble_videos_enhanced.py")],
                capture_output=True, text=True, timeout=1200
            )

            if result.returncode == 0:
                videos_dir = os.path.join(OUTPUT_DIR, "videos")
                video_count = len([f for f in os.listdir(videos_dir) if f.endswith(".mp4")]) if os.path.exists(videos_dir) else 0

                self.log_step("assemble_videos", "SUCCESS", {"videos_created": video_count})
                return True
            else:
                self.log_step("assemble_videos", "FAILED", {"stderr": result.stderr[-500:]})
                return False

        except Exception as e:
            logger.error(f"Error in step_assemble_videos: {e}", exc_info=True)
            self.log_step("assemble_videos", "ERROR", {"error": str(e)})
            return False

    def run(self, steps: list = None):
        """Run complete pipeline"""
        if steps is None:
            steps = [
                "generate_scenarios",
                "validate_scenarios",
                "generate_audio",
                "generate_frames",
                "assemble_videos"
            ]

        logger.info("\n" + "="*60)
        logger.info("VIDEO GENERATION PIPELINE STARTING")
        logger.info("="*60)

        pipeline_start = time.time()
        success_steps = 0

        for step_name in steps:
            try:
                step_method = getattr(self, f"step_{step_name}", None)
                if not step_method:
                    logger.warning(f"Step not found: {step_name}")
                    continue

                step_start = time.time()
                result = step_method()
                step_duration = time.time() - step_start

                if result:
                    success_steps += 1
                    logger.info(f"✓ {step_name} completed in {step_duration:.1f}s\n")
                else:
                    logger.error(f"✗ {step_name} failed\n")

            except Exception as e:
                logger.error(f"✗ Exception in {step_name}: {e}\n", exc_info=True)

        pipeline_duration = time.time() - pipeline_start

        self.results["end_time"] = datetime.datetime.now().isoformat()
        self.results["duration_seconds"] = pipeline_duration
        self.results["steps_completed"] = success_steps
        self.results["total_steps"] = len(steps)

        logger.info("="*60)
        logger.info("PIPELINE SUMMARY")
        logger.info("="*60)
        logger.info(f"✓ Completed: {success_steps}/{len(steps)} steps")
        logger.info(f"⏱️ Duration: {pipeline_duration:.1f} seconds")
        logger.info(f"📁 Output: {OUTPUT_DIR}")
        logger.info("="*60 + "\n")

        results_file = os.path.join(LOGS_DIR, f"pipeline_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"Results saved to {results_file}")

        return success_steps == len(steps)


def main():
    os.makedirs(LOGS_DIR, exist_ok=True)
    pipeline = Pipeline(enable_audio=ENABLE_TTS)

    steps = sys.argv[1:] if len(sys.argv) > 1 else None
    success = pipeline.run(steps)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
