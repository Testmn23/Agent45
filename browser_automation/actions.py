import logging
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

# Configure basic logging for this module
logger = logging.getLogger(__name__) # Use __name__ for module-level logger
if not logger.hasHandlers(): # Avoid adding multiple handlers if reloaded
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


async def navigate_to_url(page: Page, url: str):
    """Navigates the page to the specified URL."""
    logger.info(f"Navigating to URL: {url}")
    try:
        await page.goto(url, wait_until="networkidle", timeout=30000) # 30s timeout
        logger.info(f"Successfully navigated to {url}")
    except PlaywrightTimeoutError:
        logger.error(f"Timeout error while navigating to {url}")
        # Optionally, take a screenshot or save page source on error
        # await page.screenshot(path=f"navigate_timeout_{url.replace('/', '_')}.png")
        raise # Re-raise the exception to be handled by the executor
    except Exception as e:
        logger.error(f"Error navigating to {url}: {e}")
        raise

async def click_element(page: Page, selector: str):
    """Clicks on an element specified by its CSS selector."""
    logger.info(f"Clicking element with selector: {selector}")
    try:
        await page.locator(selector).click(timeout=10000) # 10s timeout
        logger.info(f"Successfully clicked element: {selector}")
    except PlaywrightTimeoutError:
        logger.error(f"Timeout error while trying to click element: {selector}")
        # await page.screenshot(path=f"click_timeout_{selector}.png")
        raise
    except Exception as e:
        logger.error(f"Error clicking element {selector}: {e}")
        raise

async def fill_element(page: Page, selector: str, text: str):
    """Fills an input field specified by its CSS selector with the given text."""
    logger.info(f"Filling element '{selector}' with text: '{text}'")
    try:
        await page.locator(selector).fill(text, timeout=10000) # 10s timeout
        logger.info(f"Successfully filled element '{selector}'")
    except PlaywrightTimeoutError:
        logger.error(f"Timeout error while trying to fill element: {selector}")
        # await page.screenshot(path=f"fill_timeout_{selector}.png")
        raise
    except Exception as e:
        logger.error(f"Error filling element {selector}: {e}")
        raise

async def read_element_text(page: Page, selector: str) -> str | None:
    """Reads the inner text of an element specified by its CSS selector."""
    logger.info(f"Reading text from element with selector: {selector}")
    try:
        text_content = await page.locator(selector).inner_text(timeout=5000) # 5s timeout
        logger.info(f"Successfully read text from '{selector}': '{text_content}'")
        return text_content
    except PlaywrightTimeoutError:
        logger.error(f"Timeout error while trying to read text from element: {selector}")
        # await page.screenshot(path=f"read_timeout_{selector}.png")
        return None # Or raise, depending on how critical this is
    except Exception as e:
        logger.error(f"Error reading text from element {selector}: {e}")
        return None # Or raise

async def wait_for_timeout(page: Page, milliseconds: int):
    """Waits for a specified number of milliseconds."""
    logger.info(f"Waiting for {milliseconds} milliseconds.")
    try:
        await page.wait_for_timeout(milliseconds)
        logger.info(f"Successfully waited for {milliseconds} milliseconds.")
    except Exception as e: # Should not typically fail unless Playwright itself has issues
        logger.error(f"Error during wait_for_timeout: {e}")
        raise

# Example of how these might be called by an executor (for testing purposes)
if __name__ == '__main__':
    import asyncio
    from playwright.async_api import async_playwright

    async def main_test():
        # This test requires a running browser and a page.
        # It's more of a structural example.
        # Actual testing would be done by the plan executor.
        logger.info("Running actions.py self-test example (structural).")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False) # See the browser
            page = await browser.new_page()

            try:
                # Test NAVIGATE
                await navigate_to_url(page, "https://www.example.com")

                # Test READ (example.com has an h1)
                h1_text = await read_element_text(page, "h1")
                if h1_text:
                    logger.info(f"Read H1 text: {h1_text}")

                # Test WAIT
                await wait_for_timeout(page, 2000)

                # Test NAVIGATE to a page with forms (e.g., a dummy login page)
                # For a real test, you'd need a publicly accessible or locally hosted test page.
                # This is a placeholder URL.
                await navigate_to_url(page, "https://playwright.dev/python/docs/input#input-elements")

                # Test FILL (assuming there's an input field, this will likely fail on playwright.dev)
                # On playwright.dev, there's a search bar: button[aria-label="Search"]
                # Let's try to click it first, then fill the input that appears
                await click_element(page, 'button[aria-label="Search"]')
                await wait_for_timeout(page, 1000) # wait for search modal

                # The search input is .DocSearch-Input
                await fill_element(page, 'input.DocSearch-Input', "test fill action")
                await wait_for_timeout(page, 2000)

                logger.info("Self-test example completed.")

            except Exception as e:
                logger.error(f"Error during self-test: {e}")
            finally:
                await browser.close()

    # To run this example: python browser_automation/actions.py
    # Ensure Playwright browsers are installed: playwright install
    asyncio.run(main_test())
