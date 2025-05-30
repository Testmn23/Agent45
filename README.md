# Autonomous AI Web Agent Prototype

This project is a prototype for an autonomous AI web agent. It features a Task Orchestrator that uses a Reasoning Engine (powered by an LLM) to generate multi-step plans. It also includes Browser Automation capabilities and a secure Credential Vault, designed with multi-user context in mind.

## Core Modules

-   **Task Orchestrator (`task_orchestrator/`)**:
    -   Accepts a `user_id` and a high-level task description.
    -   Invokes the Reasoning Engine to break down the task into a detailed plan.
    -   Logs the original task and the generated plan.
-   **Reasoning Engine (`reasoning_engine/`)**:
    -   Takes the task description from the Orchestrator.
    -   Uses an OpenAI GPT model (e.g., gpt-3.5-turbo) to generate a sequence of actionable steps.
    -   Returns the plan to the Orchestrator.
-   **Browser Automation (`browser_automation/`)**:
    -   Contains scripts for automating web interactions using Playwright.
    -   The `login.py` script can fetch credentials from the Credential Vault based on `user_id` and `service_name`.
-   **Credential Vault (`credential_vault/`)**:
    -   Securely stores user-specific service credentials.
    -   Credentials are encrypted using a master key (`CREDENTIAL_VAULT_KEY` stored in `.env`).
    -   Provides a CLI tool (`manage_vault.py`) for key generation and credential management.

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
    This now includes `openai` for the Reasoning Engine and `python-dotenv` for managing environment variables.

4.  **Install Playwright browser drivers:**
    ```bash
    playwright install
    ```

5.  **Configure Environment Variables (`.env` file):**
    Create a `.env` file in the project root if it doesn't exist. It should contain:

    *   **Credential Vault Master Key:**
        ```env
        # Credential Vault Master Key (KEEP THIS SECRET)
        CREDENTIAL_VAULT_KEY="your_generated_fernet_key_here"
        ```
        If you haven't generated this key yet, run:
        `python credential_vault/manage_vault.py generate-key`
        Then copy the output key into the `.env` file.
        *This might have been auto-generated in previous steps by the AI agent.*

    *   **OpenAI API Key:**
        ```env
        # OpenAI API Key for Reasoning Engine
        OPENAI_API_KEY="your_openai_api_key_here"
        ```
        Replace `your_openai_api_key_here` with your actual OpenAI API key.

6.  **Initialize the Credential Vault File:**
    After setting the `CREDENTIAL_VAULT_KEY` in `.env`, initialize the vault:
    ```bash
    python credential_vault/manage_vault.py init-vault
    ```
    *This creates `credentials.vault` and might have been done automatically.*

7.  **Add Credentials to the Vault (Example for Browser Automation):**
    For the `browser_automation/login.py` script to work, you need to add credentials it can use. The script is currently hardcoded to look for `user_id="test_user_01"` and `service_name="example_com_login"`.
    ```bash
    python credential_vault/manage_vault.py add-credential test_user_01 example_com_login your_web_username your_web_password
    ```

## Running the Prototype

### Task Orchestrator (with Plan Generation)

The Task Orchestrator now generates a plan using the LLM. Ensure your `OPENAI_API_KEY` is correctly set in `.env`.

```bash
python task_orchestrator/main.py test_user_01 "Log into example.com and check my messages."
```
Output will include the original task and the generated multi-step plan. If the API key is missing or invalid, a warning will be logged.

### Browser Automation (Login Script)

This script demonstrates logging into a website using credentials from the vault.

1.  **Prerequisites:**
    *   `.env` file configured with `CREDENTIAL_VAULT_KEY` (and `OPENAI_API_KEY` for other parts of the system, though not directly by `login.py`).
    *   Vault initialized and credentials for `test_user_01`/`example_com_login` added (see Setup Step 7).
    *   **Crucial:** Update HTML selectors and `DEFAULT_LOGIN_URL` in `browser_automation/login.py` to match a real website.

2.  **Run:**
    ```bash
    python browser_automation/login.py
    ```

### Credential Vault Management

Use `manage_vault.py` for key generation and credential management:
```bash
# Generate a new master key for the vault
python credential_vault/manage_vault.py generate-key

# Initialize an empty vault file (after setting the key in .env)
python credential_vault/manage_vault.py init-vault

# Add/update a credential
python credential_vault/manage_vault.py add-credential <user_id> <service_name> <username> <password>

# Retrieve a credential (for testing)
python credential_vault/manage_vault.py get-credential <user_id> <service_name>
```

## Next Steps Roadmap

1.  ~~Prototype Task Orchestrator + simple Playwright login to test credential flow.~~
2.  ~~Refine for multi-user & security (Credential Vault).~~
3.  **Integrate LLM for generating multi-step plans.** (Current phase: Basic plan generation implemented)
4.  Add Captcha Solver to handle test challenges.
5.  Build the Concurrency Scheduler (Celery + Redis).
6.  Develop individual Task Modules (start with GitHub push), which would execute the plans from the Reasoning Engine.
7.  Containerize and deploy a minimal end-to-end on a cloud VM.
EOF
