import asyncio
import logging
import os
import sys

# Add project root to sys.path to allow importing credential_vault
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from playwright.async_api import async_playwright
from credential_vault import vault # Import the vault module

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Placeholder selectors - these will vary greatly depending on the website
# These should ideally be configured per service_name or passed in.
# For this example, we'll keep them global but acknowledge they need to be specific.
USERNAME_SELECTOR = "#username"  # Replace with the actual selector for the username field
PASSWORD_SELECTOR = "#password"  # Replace with the actual selector for the password field
LOGIN_BUTTON_SELECTOR = "#loginButton" # Replace with the actual selector for the login button
SUCCESS_SELECTOR = "#dashboard" # Replace with a selector that appears after successful login
# Placeholder for the login URL, this might also come from a config or the vault per service
DEFAULT_LOGIN_URL = "https://example.com/login" # Replace with a real login page for testing

async def login_and_check(user_id: str, service_name: str, login_url: str):
    """
    Navigates to a login page, attempts to log in using credentials
    from the vault, and checks for success.
    """
    logging.info(f"Attempting login for user '{user_id}' on service '{service_name}' at URL '{login_url}'")

    username, password = vault.get_credential(user_id, service_name)

    if not username or not password:
        logging.error(f"Could not retrieve credentials for user '{user_id}', service '{service_name}' from vault.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # Set headless=False to watch execution
        page = await browser.new_page()
        try:
            logging.info(f"Navigating to {login_url}")
            await page.goto(login_url, wait_until="networkidle")

            logging.info(f"Attempting to fill username: {username}")
            await page.fill(USERNAME_SELECTOR, username)

            logging.info("Attempting to fill password")
            await page.fill(PASSWORD_SELECTOR, password) # Password is plain text here after decryption

            logging.info("Attempting to click login button")
            await page.click(LOGIN_BUTTON_SELECTOR)

            await page.wait_for_selector(SUCCESS_SELECTOR, timeout=5000) # 5 seconds timeout
            logging.info(f"Login appears successful for user '{user_id}' on service '{service_name}'.")
            # await page.screenshot(path=f"{user_id}_{service_name}_login_success.png")

        except Exception as e:
            logging.error(f"Login failed for user '{user_id}' on service '{service_name}': {e}")
            # await page.screenshot(path=f"{user_id}_{service_name}_login_failure.png")
        finally:
            await browser.close()

async def main():
    # For demonstration, these values would typically come from the orchestrator
    test_user_id = "test_user_01"
    # This service_name should match what's used when storing credentials via manage_vault.py
    test_service_name = "example_com_login"
    test_login_url = DEFAULT_LOGIN_URL # Using the default, could be service-specific

    # Before running this, ensure:
    # 1. CREDENTIAL_VAULT_KEY is in .env
    # 2. The vault is initialized (e.g., python credential_vault/manage_vault.py init-vault)
    # 3. Credentials for test_user_id and test_service_name are added via manage_vault.py
    #    Example:
    #    python credential_vault/manage_vault.py add-credential test_user_01 example_com_login your_username your_password

    if not os.environ.get(vault.ENV_VAULT_KEY):
        logging.error(f"Error: The {vault.ENV_VAULT_KEY} environment variable is not set.")
        logging.error("Please ensure it's in your .env file and valid.")
        return

    logging.info("Attempting to initialize vault (if not already done by a previous vault operation)")
    try:
        vault.initialize_vault_file_if_not_exists() # Good practice to call this
    except Exception as e:
        logging.error(f"Failed to initialize vault: {e}")
        return

    await login_and_check(test_user_id, test_service_name, test_login_url)

if __name__ == "__main__":
    # Playwright browsers should already be installed from previous steps.
    asyncio.run(main())
