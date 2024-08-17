import asyncio
from playwright.async_api import async_playwright, Playwright

async def get_browser(playwright: Playwright):
    chrome = playwright.devices["Desktop Chrome"]
    browser = await playwright.webkit.launch(headless=False)
    context = await browser.new_context(
        **chrome,
    )
    await context.route("**/*", lambda route, request: route.abort() if request.resource_type in ["image", "media"] else route.continue_())

async def main():
    async with async_playwright() as playwright:
        await get_browser(playwright)
asyncio.run(main())