import logging
import argparse

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def accept_task(user_id: str, task_description: str):
    """
    Accepts a user ID and task description, then logs them.
    In the future, this function will also dispatch the task to a scheduler.
    """
    logging.info(f"Task received for user_id '{user_id}': {task_description}")
    # Placeholder for dispatching to a scheduler
    # print(f"Dispatching task for user '{user_id}' to scheduler (not implemented yet)...")

def main():
    parser = argparse.ArgumentParser(description="Task Orchestrator")
    parser.add_argument("user_id", type=str, help="The ID of the user initiating the task.")
    parser.add_argument("task_description", type=str, help="A description of the task to be executed.")
    args = parser.parse_args()

    accept_task(args.user_id, args.task_description)

if __name__ == "__main__":
    main()
