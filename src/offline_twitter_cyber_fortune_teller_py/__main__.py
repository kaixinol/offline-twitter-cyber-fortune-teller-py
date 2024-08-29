import asyncio
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright, TimeoutError
from rich.progress import track
from rich.prompt import Prompt, Confirm
from tqdm.asyncio import tqdm

from . import data_folder, config, xpath
from .lock import update
from .spider import crawl_profile


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
        browser = await pw.chromium.launch_persistent_context(
            user_data_dir=data_folder, headless=False
        )
        main_page = browser.pages[0]
        username = Prompt.ask("What's your username?(e.g. @jack or jack)")
        if not username:
            print("Please enter your username!")
        await main_page.goto(f"https://x.com/{username}")
        available_page = []
        pages = set()
        for _ in track(range(config.thread), description="Preparing..", transient=True):
            _ = await browser.new_page()
            update({id(_): False})
            available_page.append(_)
        user_profile = await crawl_profile(main_page)
        progress = tqdm(
            total=min(50, user_profile.tweet_count),
            desc="Get tweet links that meet the requirements",
            leave=False,
            unit="tweet",
        )
        num = 0
        while not (num := num + 1) >= min(50, user_profile.tweet_count):
            await main_page.evaluate("window.scrollBy(0, 300)")
            await main_page.locator(xpath.tweet.link).last.wait_for(state="visible")

            async def get_tweet_link(element) -> list[tuple[datetime, str]]:
                ret = []
                for i in element:
                    try:
                        ret.append(
                            (
                                datetime.fromisoformat(
                                    (
                                        await i.locator("time").get_attribute(
                                            "datetime"
                                        )
                                    ).rstrip("Z")
                                ),
                                await i.get_attribute("href"),
                            )
                        )
                    except TimeoutError:
                        continue
                return ret

            _ = await main_page.locator(xpath.tweet.link).all()
            _ = set(await get_tweet_link(_))
            progress.update(len(_ - pages))
            pages |= _
            await asyncio.sleep(1)
        progress.close()
        ordered_pages = list(pages)
        ordered_pages.sort(key=lambda x: x[0])
        print(ordered_pages)


asyncio.run(main())
