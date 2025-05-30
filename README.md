# Autonomous AI Web Agent Prototype

This project is a prototype for an autonomous AI web agent, focusing initially on a Task Orchestrator and Browser Automation capabilities.

## Modules

- **Task Orchestrator (`task_orchestrator/`)**: Accepts task descriptions and logs them. Future development will include dispatching tasks to a scheduler.
- **Browser Automation (`browser_automation/`)**: Contains scripts for automating web interactions using Playwright. Includes a basic login script.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Playwright browser drivers:**
    ```bash
    playwright install
    ```
    (You might need to specify a browser, e.g., `playwright install chromium`)

5.  **Configure Environment Variables:**
    Copy the existing `.env` file (if it wasn't created by you, it might be empty or have other settings) or create one if it doesn't exist. Add your actual credentials and target URL:
    ```env
    # Browser Automation Credentials
    LOGIN_URL="your_login_url_here"
    USERNAME="your_actual_username"
    PASSWORD="your_actual_password"
    ```
    *Note: The current `browser_automation/login.py` script uses hardcoded placeholders. Future versions will integrate with these environment variables.*

## Running the Prototype

### Task Orchestrator

To run the task orchestrator, navigate to its directory and execute the `main.py` script with a task description:

```bash
python task_orchestrator/main.py "Order a pizza from Domino's"
```
This will log the received task.

### Browser Automation (Login Script)

To run the login script:

1.  **Important:** The current `browser_automation/login.py` script has **hardcoded placeholders** for the URL, username, password, and HTML selectors. You **MUST** update these placeholders directly in the script to point to a real login page and use valid credentials and selectors for it to work.
    - `LOGIN_URL`
    - `USERNAME`
    - `PASSWORD`
    - `USERNAME_SELECTOR`
    - `PASSWORD_SELECTOR`
    - `LOGIN_BUTTON_SELECTOR`
    - `SUCCESS_SELECTOR` (element to check for successful login)

2.  Once the script is configured, run it from the `browser_automation` directory:
    ```bash
    python browser_automation/login.py
    ```
    The script will attempt to log in to the specified website. Check the console output for success or error messages. Logs and screenshots (on failure/success, if enabled in code) might be saved in the `browser_automation` directory.

## Next Steps (from original issue)

1.  Prototype Task Orchestrator + simple Playwright login to test credential flow. (Current focus)
2.  Integrate LLM for generating multi-step plans.
3.  Add Captcha Solver to handle test challenges.
4.  Build the Concurrency Scheduler (Celery + Redis).
5.  Develop individual Task Modules (start with GitHub push).
6.  Containerize and deploy a minimal end-to-end on a cloud VM.
```
