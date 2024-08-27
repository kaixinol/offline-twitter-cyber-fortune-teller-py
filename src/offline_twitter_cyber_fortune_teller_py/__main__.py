import asyncio
from pathlib import Path

from playwright.async_api import async_playwright
from . import data_folder
from rich.prompt import Confirm


async def set_cookie():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch_persistent_context(
            user_data_dir=data_folder, headless=False
        )
        page = browser.pages[0]
        await page.goto("https://x.com/home")
        input("Press Enter if you are already logged in")


async def main():
    def is_empty_dir(directory: Path) -> bool:
        if directory.is_dir():
            return not any(directory.iterdir())
        else:
            raise NotADirectoryError(f"{directory} 不是一个目录")

    if not Confirm.ask(
        "Have you logged in to X (Twitter)?", default=not is_empty_dir(data_folder)
    ):
        await set_cookie()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch_persistent_context(user_data_dir=data_folder)
        page = browser.pages[0]
        username = Confirm.ask("What's your username?(e.g. @jack or jack)")
        if not username:
            print("Please enter your username!")
        await page.goto(f"https://x.com/{username}")


asyncio.run(main())
