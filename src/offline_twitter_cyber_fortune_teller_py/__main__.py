from datetime import datetime
from pathlib import Path
import asyncio

from playwright.async_api import async_playwright, TimeoutError, Page
from rich.progress import track
from rich.prompt import Prompt, Confirm
from tqdm.asyncio import tqdm

from . import data_folder, config, xpath
from .lock import update, get
from .spider import crawl_profile, crawl_tweet


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
        while not username:
            print("Please enter your username!")
            Prompt.ask("What's your username?(e.g. @jack or jack)")
        await main_page.route(
            "**/*",
            lambda route, request: route.abort()
            if request.resource_type in ["image", "media"]
            else route.continue_(),
        )
        await main_page.goto(f"https://x.com/{username}")
        available_page = []
        pages = set()
        for _ in track(range(config.thread), description="Preparing..", transient=True):
            _ = await browser.new_page()
            await update({id(_): False})
            available_page.append(_)
        user_profile = await crawl_profile(main_page)
        progress = tqdm(
            total=min(config.pages, user_profile.tweet_count),
            desc="Get tweet links that meet the requirements",
            leave=False,
            unit="tweet",
        )
        num = 0
        while not (num := num + 1) >= min(config.pages, user_profile.tweet_count):
            await main_page.evaluate("window.scrollBy(0, 300)")
            await main_page.locator(xpath.tweet.link).last.wait_for(
                state="visible", timeout=10000
            )

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

            async def get_available_page() -> Page:
                available_pages = [
                    page
                    for i, using in (await get()).items()
                    if not using
                    for page in available_page
                    if id(page) == i
                ]
                if available_pages:
                    await update({id(available_pages[0]): True})
                    return available_pages[0]
                await asyncio.sleep(
                    (lambda x: 4000 // (2**x) if x <= 2 else 0)(len(available_pages))
                )
                return await get_available_page()

            _ = await main_page.locator(xpath.tweet.link).all()
            _ = set(await get_tweet_link(_))
            progress.update(len(_ - pages))
            pages |= _
            await asyncio.sleep(0.1)
        progress.close()
        ordered_pages = [(time, "https://x.com" + link) for time, link in pages]
        ordered_pages.sort(key=lambda x: x[0])
        progress = tqdm(
            total=len(ordered_pages),
            desc="Extracting information from tweets",
            leave=False,
            unit="tweet",
        )
        tasks = [
            asyncio.create_task(crawl_tweet(get_available_page, i, progress))
            for i in ordered_pages
        ]
        done, pending = await asyncio.wait(
            tasks, timeout=30, return_when=asyncio.ALL_COMPLETED
        )

        # 处理超时任务
        for task in pending:
            task.cancel()
            print("A task was cancelled due to timeout")

        results = [task.result() for task in done]
        print(results)


asyncio.run(main())
