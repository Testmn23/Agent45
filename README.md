# Autonomous AI Web Agent Prototype

This project is a prototype for an autonomous AI web agent, focusing initially on a Task Orchestrator, Browser Automation, and a secure Credential Vault. The system is being built with multi-user capabilities in mind.

## Modules

-   **Task Orchestrator (`task_orchestrator/`)**: Accepts task descriptions along with a `user_id` and logs them. Future development will include dispatching tasks to a scheduler.
-   **Browser Automation (`browser_automation/`)**: Contains scripts for automating web interactions using Playwright. The login script now fetches credentials from the Credential Vault based on `user_id` and `service_name`.
-   **Credential Vault (`credential_vault/`)**: Securely stores user-specific service credentials, encrypted using a master key.

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

5.  **Configure Environment Variables & Vault Setup:**
    *   The system uses a `.env` file for environment-specific configurations.
    *   **Master Encryption Key for Vault**: The Credential Vault requires a master encryption key.
        1.  Generate a new key:
            ```bash
            python credential_vault/manage_vault.py generate-key
            ```
        2.  Copy the generated key.
        3.  Create or open your `.env` file in the project root.
        4.  Add the key to your `.env` file like this (replace `your_generated_fernet_key_here` with the actual key):
            ```env
            CREDENTIAL_VAULT_KEY="your_generated_fernet_key_here"
            ```
            *This key was automatically generated and added if you followed the previous steps with the AI agent.*
    *   **Initialize the Vault File**: After setting the `CREDENTIAL_VAULT_KEY`, initialize the encrypted vault file:
        ```bash
        python credential_vault/manage_vault.py init-vault
        ```
        This creates an empty `credentials.vault` file, ready to store credentials. *This might have also been done automatically by the agent or upon first use by other scripts if the key was set.*

6.  **Add Credentials to the Vault:**
    Use the `manage_vault.py` script to add credentials that the browser automation script will use.
    For example, to add credentials for `test_user_01` for a service named `example_com_login`:
    ```bash
    python credential_vault/manage_vault.py add-credential test_user_01 example_com_login your_actual_username your_actual_password
    ```
    Replace `your_actual_username` and `your_actual_password` accordingly. The `service_name` (`example_com_login` in this case) is how the login script will request these specific credentials.

## Running the Prototype

### Task Orchestrator

To run the task orchestrator, provide a `user_id` and a task description:

```bash
python task_orchestrator/main.py test_user_01 "Order a pizza from Domino's"
```
This will log the received task along with the user ID.

### Browser Automation (Login Script)

The `browser_automation/login.py` script is set up to demonstrate logging in for a pre-configured user (`test_user_01`) and service (`example_com_login`).

1.  **Ensure Prerequisites:**
    *   `.env` file exists with a valid `CREDENTIAL_VAULT_KEY`.
    *   Vault is initialized (`python credential_vault/manage_vault.py init-vault`).
    *   Credentials for `test_user_01` and `example_com_login` are added to the vault as shown in step 6 of Setup.
    *   **Critical:** The HTML selectors within `browser_automation/login.py` (`USERNAME_SELECTOR`, `PASSWORD_SELECTOR`, etc.) and the `DEFAULT_LOGIN_URL` must be updated to point to a real, accessible login page for the script to function correctly.

2.  **Run the script:**
    ```bash
    python browser_automation/login.py
    ```
    The script will attempt to fetch credentials from the vault for `test_user_01` / `example_com_login` and log in. Check the console output.

## Next Steps (from original issue)

The overall project aims to build a modular, cloud-native architecture for autonomous AI web agents.

1.  ~~Prototype Task Orchestrator + simple Playwright login to test credential flow.~~ (Partially addressed, now with basic vault)
2.  **Refine for multi-user & security (current focus):**
    *   ~~Design and implement Credential Vault.~~ (Done for prototype)
    *   Integrate vault with Task Orchestrator and Browser Automation. (Done for prototype)
3.  Integrate LLM for generating multi-step plans.
4.  Add Captcha Solver to handle test challenges.
5.  Build the Concurrency Scheduler (Celery + Redis).
6.  Develop individual Task Modules (start with GitHub push).
7.  Containerize and deploy a minimal end-to-end on a cloud VM.
```
