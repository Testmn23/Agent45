import os
import logging
from openai import OpenAI, OpenAIError

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fetch API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY environment variable not found. Reasoning engine will not function.")
    # You could raise an error here, but for now, let's allow the module to load
    # and have generate_plan fail gracefully.
    # raise ValueError("OPENAI_API_KEY environment variable not set.")

client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        logging.error(f"Failed to initialize OpenAI client: {e}")
        client = None # Ensure client is None if initialization fails

def generate_plan(user_id: str, task_description: str) -> list[str]:
    """
    Generates a multi-step plan for a given task description using an LLM.

    Args:
        user_id: The ID of the user (currently for logging and future context).
        task_description: The high-level task from the user.

    Returns:
        A list of strings, where each string is a step in the plan.
        Returns an empty list if plan generation fails or API key is missing.
    """
    if not client:
        logging.error("OpenAI client not initialized. Cannot generate plan. Missing API key or initialization failed.")
        return []

    logging.info(f"Generating plan for user_id '{user_id}' with task: {task_description}")

    system_message = "You are an expert web automation assistant. Your task is to break down a user's request into a series of simple, actionable steps that can be performed by a browser automation tool like Playwright. Each step should be a clear instruction. Do not number the steps. Each step should be on a new line. Focus on concrete actions a user would take in a browser."

    user_prompt = f"Task: {task_description}"

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Or another model like "gpt-4"
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,  # Adjust for creativity vs. determinism
        )

        raw_plan = completion.choices[0].message.content
        if raw_plan:
            # Split by newline and filter out any empty strings
            plan_steps = [step.strip() for step in raw_plan.split('\n') if step.strip()]
            logging.info(f"Generated plan: {plan_steps}")
            return plan_steps
        else:
            logging.warning("LLM returned an empty plan.")
            return []

    except OpenAIError as e:
        logging.error(f"OpenAI API error during plan generation: {e}")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred during plan generation: {e}")
        return []

if __name__ == '__main__':
    # Example usage (requires OPENAI_API_KEY to be set in .env and loaded)
    if not OPENAI_API_KEY:
        print("Please set your OPENAI_API_KEY in the .env file and ensure it's loaded to run this example.")
    else:
        print("Attempting to load .env variables for example...")
        # Quick and dirty way to load .env for direct script execution,
        # not for production module use.
        # In a real app, .env is loaded at the entry point.
        try:
            from dotenv import load_dotenv
            # Construct the .env path relative to this script's location
            dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
            if os.path.exists(dotenv_path):
                load_dotenv(dotenv_path=dotenv_path)
            else:
                print(f".env file not found at {dotenv_path}. Skipping load_dotenv.")

            # Re-check API key after attempting to load .env
            OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
            if OPENAI_API_KEY and client is None: # If client failed before due to no key
                 client = OpenAI(api_key=OPENAI_API_KEY)

            if not OPENAI_API_KEY or client is None:
                 print("Failed to load OPENAI_API_KEY or initialize client even after .env attempt.")
            else:
                test_user = "test_user_llm"
                # test_task = "Order a large pepperoni pizza from Pizza Hut for delivery to 123 Main St, Anytown, USA."
                test_task = "Log into GitHub and create a new repository called 'my-awesome-project'."

                print(f"--- Running Test ---")
                print(f"User: {test_user}")
                print(f"Task: {test_task}")

                plan = generate_plan(test_user, test_task)

                if plan:
                    print("\n--- Generated Plan ---")
                    for i, step in enumerate(plan):
                        print(f"{i+1}. {step}")
                else:
                    print("\n--- No plan generated or error occurred ---")

        except ImportError:
            print("python-dotenv is not installed. Skipping .env loading for example.")
            print("Ensure OPENAI_API_KEY is available in your environment if you run this directly.")
        except Exception as e:
            print(f"Error during example run: {e}")
