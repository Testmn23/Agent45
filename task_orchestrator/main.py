import logging
import argparse
import os
import sys
import asyncio # Required for async Playwright operations

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from reasoning_engine import engine as reasoning_engine
from task_orchestrator import plan_executor # Import the plan executor
from playwright.async_api import async_playwright, Playwright

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Reduce Playwright's own logger level if it's too verbose
logging.getLogger("playwright").setLevel(logging.WARNING)


async def launch_browser_and_execute_plan(user_id: str, task_description: str, plan: list[str]):
    """
    Launches a Playwright browser session and executes the given plan.
    """
    async with async_playwright() as p:
        browser = None
        try:
            # browser = await p.chromium.launch(headless=False) # For debugging, show browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # service_name can be derived or passed; using task_description for now for context
            await plan_executor.execute_plan(user_id, task_description, plan, page)

            logging.info(f"Plan execution completed for user '{user_id}'.")

        except Exception as e:
            logging.error(f"An error occurred during plan execution for user '{user_id}': {e}")
            # Screenshots or other cleanup could happen here
            # if page and not page.is_closed():
            #     await page.screenshot(path=f"error_screenshot_{user_id}.png")
        finally:
            if browser:
                await browser.close()
            logging.info(f"Browser session closed for user '{user_id}'.")


async def accept_and_execute_task(user_id: str, task_description: str):
    """
    Accepts a task, generates a plan, and then executes the plan.
    """
    logging.info(f"Task received for user_id '{user_id}': {task_description}")

    plan = reasoning_engine.generate_plan(user_id, task_description)

    if plan:
        logging.info(f"Generated plan for user_id '{user_id}':")
        for i, step in enumerate(plan):
            logging.info(f"  Step {i+1}: {step}")

        # Now, execute the plan
        await launch_browser_and_execute_plan(user_id, task_description, plan)

    else:
        logging.warning(f"No plan generated for user_id '{user_id}'. Task: '{task_description}'")
        logging.warning("This could be due to a missing/invalid OPENAI_API_KEY or an issue with the LLM.")


async def main_async(): # Renamed main to main_async to use asyncio.run
    parser = argparse.ArgumentParser(description="Task Orchestrator")
    parser.add_argument("user_id", type=str, help="The ID of the user initiating the task.")
    parser.add_argument("task_description", type=str, help="A description of the task to be executed.")
    args = parser.parse_args()

    try:
        from dotenv import load_dotenv
        dotenv_path = os.path.join(project_root, '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path=dotenv_path)
            logging.info(f"Loaded .env file from {dotenv_path}")
        else:
            logging.info(".env file not found, relying on environment-set variables.")
    except ImportError:
        logging.info("python-dotenv not installed. Relying on environment-set variables.")
    except Exception as e:
        logging.error(f"Error loading .env: {e}")

    await accept_and_execute_task(args.user_id, args.task_description)

if __name__ == "__main__":
    # Ensure Playwright browsers are installed (usually done once)
    # e.g., via `playwright install` in the terminal
    asyncio.run(main_async())
