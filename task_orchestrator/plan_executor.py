import logging
import re
import sys
import os
from playwright.async_api import Page

# Add project root to sys.path to allow importing browser_automation
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from browser_automation import actions as browser_actions

# Configure basic logging for this module
logger = logging.getLogger(__name__)
if not logger.hasHandlers(): # Avoid adding multiple handlers if reloaded
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Define regex patterns for parsing plan steps
ACTION_PATTERNS = {
    "NAVIGATE": re.compile(r"^NAVIGATE\s+(https?://\S+)", re.IGNORECASE),
    "CLICK": re.compile(r"^CLICK\s+([a-zA-Z0-9_#\-\.\s\[\]\"=:>]+)", re.IGNORECASE), # More flexible selector
    "FILL": re.compile(r"^FILL\s+([a-zA-Z0-9_#\-\.\s\[\]\"=:>]+)\s+WITH\s+(.+)", re.IGNORECASE),
    "READ": re.compile(r"^READ\s+([a-zA-Z0-9_#\-\.\s\[\]\"=:>]+)", re.IGNORECASE),
    "WAIT": re.compile(r"^WAIT\s+(\d+)", re.IGNORECASE),
}

def parse_step(step: str) -> tuple[str | None, dict]:
    """
    Parses a plan step string into an action keyword and arguments.

    Args:
        step: A single plan step string (e.g., "NAVIGATE https://example.com").

    Returns:
        A tuple (action_keyword, arguments_dict) or (None, {}) if parsing fails.
        Example: ("NAVIGATE", {"url": "https://example.com"})
                 ("FILL", {"selector": "input#user", "text": "test"})
    """
    step = step.strip()
    for keyword, pattern in ACTION_PATTERNS.items():
        match = pattern.match(step)
        if match:
            if keyword == "NAVIGATE":
                return keyword, {"url": match.group(1).strip()}
            elif keyword == "CLICK":
                return keyword, {"selector": match.group(1).strip()}
            elif keyword == "FILL":
                # Group 2 might need stripping of quotes if LLM adds them,
                # but for now, take raw.
                return keyword, {"selector": match.group(1).strip(), "text": match.group(2).strip()}
            elif keyword == "READ":
                return keyword, {"selector": match.group(1).strip()}
            elif keyword == "WAIT":
                return keyword, {"milliseconds": int(match.group(1))}
            # Add other keywords here
    logger.warning(f"Could not parse step: '{step}'")
    return None, {}

async def execute_plan(user_id: str, service_name: str, plan: list[str], page: Page):
    """
    Executes a list of plan steps using the browser automation actions.

    Args:
        user_id: ID of the user, for logging/context.
        service_name: Name of the service, for logging/context.
        plan: A list of plan step strings.
        page: An active Playwright Page object.
    """
    logger.info(f"Executing plan for user '{user_id}' on service '{service_name}': {len(plan)} steps.")

    for i, step_str in enumerate(plan):
        logger.info(f"Executing step {i+1}/{len(plan)}: {step_str}")
        action, args = parse_step(step_str)

        if not action:
            logger.error(f"Skipping unparseable step: {step_str}")
            continue # Or you could raise an error / stop execution

        try:
            if action == "NAVIGATE":
                await browser_actions.navigate_to_url(page, args["url"])
            elif action == "CLICK":
                await browser_actions.click_element(page, args["selector"])
            elif action == "FILL":
                await browser_actions.fill_element(page, args["selector"], args["text"])
            elif action == "READ":
                # The result of read_element_text is currently just logged by the action itself.
                # Future enhancements could store this in a context dictionary.
                await browser_actions.read_element_text(page, args["selector"])
            elif action == "WAIT":
                await browser_actions.wait_for_timeout(page, args["milliseconds"])
            else:
                logger.warning(f"Unknown action keyword: {action}. Skipping step.")
                # This case should ideally not be hit if parse_step only returns known actions

        except Exception as e:
            logger.error(f"Error executing step '{step_str}': {e}")
            # Decide on error strategy: stop plan, skip step, or retry?
            # For now, we'll log and continue, but in a real scenario, might stop.
            # Optionally, take a screenshot on error
            # await page.screenshot(path=f"error_step_{i+1}.png")
            # Consider re-raising to let the orchestrator know the plan failed.
            # For this iteration, let's re-raise to make failure explicit
            raise # Re-raise the exception to stop plan execution on first error

    logger.info(f"Successfully executed plan for user '{user_id}' on service '{service_name}'.")


if __name__ == '__main__':
    # Example Usage for testing parse_step and execute_plan (conceptually)

    # Test parse_step
    print("--- Testing parse_step ---")
    test_steps = [
        "NAVIGATE https://example.com",
        "CLICK button#submit",
        "FILL input[name='email'] WITH test@example.com",
        "FILL textarea#bio WITH This is a longer text.",
        "READ div.classname",
        "WAIT 1000",
        "INVALID STEP",
        "CLICK a.link[href*='product'] > span" # More complex selector
    ]
    for ts in test_steps:
        action, args_dict = parse_step(ts)
        print(f"Step: '{ts}' -> Action: '{action}', Args: {args_dict}")

    # Conceptual test for execute_plan (requires running browser, etc.)
    # This part won't run directly but shows structure.
    async def main_executor_test():
        logger.info("Conceptual test for execute_plan (does not launch browser here).")
        # In a real test, you'd set up a Playwright page object.
        # from playwright.async_api import async_playwright
        # async with async_playwright() as p:
        #     browser = await p.chromium.launch(headless=False)
        #     page = await browser.new_page()
        #     try:
        #         sample_plan = [
        #             "NAVIGATE https://example.com",
        #             "READ h1",
        #             "WAIT 2000"
        #         ]
        #         await execute_plan("test_user", "example_service", sample_plan, page)
        #     finally:
        #         await browser.close()
        pass # Placeholder

    # asyncio.run(main_executor_test()) # Would run the conceptual test
    print("\n--- Plan Executor module loaded ---")
    print("Run task_orchestrator/main.py to see this in action with a browser.")

EOF
