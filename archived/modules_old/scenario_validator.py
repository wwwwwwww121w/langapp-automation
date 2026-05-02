import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class ScenarioValidator:
    """Validates video scenario structure and content quality"""

    REQUIRED_FIELDS = ["id", "type", "hook_en", "hook_ar", "items", "cta_en", "cta_ar", "hashtags"]
    ITEM_REQUIRED_FIELDS = ["en", "ar"]
    VALID_TYPES = ["fact", "dialect", "mistake", "phrase"]
    MIN_ITEMS = 2
    MAX_ITEMS = 6

    @staticmethod
    def validate_scenario(scenario: dict) -> Tuple[bool, List[str]]:
        """
        Validate a scenario. Returns (is_valid, error_messages)
        """
        errors = []

        if not isinstance(scenario, dict):
            return False, ["Scenario must be a dictionary"]

        for field in ScenarioValidator.REQUIRED_FIELDS:
            if field not in scenario:
                errors.append(f"Missing required field: {field}")

        if "type" in scenario and scenario["type"] not in ScenarioValidator.VALID_TYPES:
            errors.append(f"Invalid type: {scenario['type']}. Must be one of {ScenarioValidator.VALID_TYPES}")

        if "hook_en" in scenario:
            if not isinstance(scenario["hook_en"], str) or len(scenario["hook_en"]) < 5:
                errors.append("hook_en must be a string with at least 5 characters")
            if len(scenario["hook_en"]) > 150:
                errors.append("hook_en must be less than 150 characters")

        if "hook_ar" in scenario:
            if not isinstance(scenario["hook_ar"], str) or len(scenario["hook_ar"]) < 3:
                errors.append("hook_ar must be a string with at least 3 characters")

        if "items" in scenario:
            if not isinstance(scenario["items"], list):
                errors.append("items must be a list")
            elif len(scenario["items"]) < ScenarioValidator.MIN_ITEMS:
                errors.append(f"items must have at least {ScenarioValidator.MIN_ITEMS} items")
            elif len(scenario["items"]) > ScenarioValidator.MAX_ITEMS:
                errors.append(f"items must have at most {ScenarioValidator.MAX_ITEMS} items")
            else:
                for i, item in enumerate(scenario["items"]):
                    item_errors = ScenarioValidator._validate_item(item, i)
                    errors.extend(item_errors)

        if "cta_en" in scenario and (not isinstance(scenario["cta_en"], str) or len(scenario["cta_en"]) < 5):
            errors.append("cta_en must be a string with at least 5 characters")

        if "cta_ar" in scenario and (not isinstance(scenario["cta_ar"], str) or len(scenario["cta_ar"]) < 3):
            errors.append("cta_ar must be a string with at least 3 characters")

        if "hashtags" in scenario:
            if not isinstance(scenario["hashtags"], list):
                errors.append("hashtags must be a list")
            elif len(scenario["hashtags"]) == 0:
                errors.append("hashtags list cannot be empty")

        return len(errors) == 0, errors

    @staticmethod
    def _validate_item(item: dict, index: int) -> List[str]:
        """Validate a single item"""
        errors = []

        if not isinstance(item, dict):
            errors.append(f"Item {index} must be a dictionary")
            return errors

        for field in ScenarioValidator.ITEM_REQUIRED_FIELDS:
            if field not in item:
                errors.append(f"Item {index} missing required field: {field}")

        if "en" in item:
            if not isinstance(item["en"], str) or len(item["en"]) < 2:
                errors.append(f"Item {index} 'en' must be a non-empty string")

        if "ar" in item:
            if not isinstance(item["ar"], str) or len(item["ar"]) < 2:
                errors.append(f"Item {index} 'ar' must be a non-empty string")

        return errors

    @staticmethod
    def validate_scenarios(scenarios: List[dict]) -> Tuple[List[dict], List[dict]]:
        """
        Validate a list of scenarios.
        Returns (valid_scenarios, invalid_scenarios_with_errors)
        """
        valid = []
        invalid = []

        for scenario in scenarios:
            is_valid, errors = ScenarioValidator.validate_scenario(scenario)
            if is_valid:
                valid.append(scenario)
            else:
                invalid.append({"scenario": scenario, "errors": errors})
                logger.warning(f"Invalid scenario {scenario.get('id', 'unknown')}: {errors}")

        return valid, invalid

    @staticmethod
    def fix_scenario(scenario: dict) -> dict:
        """Attempt to fix common issues in a scenario"""
        fixed = scenario.copy()

        if not isinstance(fixed.get("items"), list):
            fixed["items"] = []

        if not fixed.get("hashtags"):
            fixed["hashtags"] = ["#learnarabic", "#english"]

        if not fixed.get("type"):
            fixed["type"] = "phrase"

        if isinstance(fixed.get("hook_en"), str):
            fixed["hook_en"] = fixed["hook_en"][:150]

        return fixed
