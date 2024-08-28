import asyncio
from pathlib import Path

from playwright.async_api import async_playwright
from . import data_folder, config
from rich.prompt import Prompt, Confirm
from rich.progress import track
from .lock import update


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
        main_page = browser.pages[0]
        username = Prompt.ask("What's your username?(e.g. @jack or jack)")
        if not username:
            print("Please enter your username!")
        await main_page.goto(f"https://x.com/{username}")
        available_page = []

        for _ in track(
            range(config.thread),
            description="Preparing..",
        ):
            _ = await browser.new_page()
            update({id(_): False})
            available_page.append(_)


asyncio.run(main())
