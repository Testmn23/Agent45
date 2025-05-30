import logging
import argparse

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def accept_task(task_description: str):
    """
    Accepts a task description and logs it.
    In the future, this function will also dispatch the task to a scheduler.
    """
    logging.info(f"Task received: {task_description}")
    # Placeholder for dispatching to a scheduler
    # print("Dispatching to scheduler (not implemented yet)...")

def main():
    parser = argparse.ArgumentParser(description="Task Orchestrator")
    parser.add_argument("task_description", type=str, help="A description of the task to be executed.")
    args = parser.parse_args()

    accept_task(args.task_description)

if __name__ == "__main__":
    main()
