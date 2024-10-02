from datetime import datetime
from pathlib import Path
import asyncio
from time import sleep

from playwright.async_api import async_playwright, TimeoutError
from rich.progress import track
from rich.prompt import Prompt, Confirm
from tqdm.asyncio import tqdm

from . import data_folder, config, xpath
from .spider import crawl_profile, crawl_tweet
from .analyzer import parse_to_str, run


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
            available_page.append(_)
        user_profile = await crawl_profile(main_page)
        progress = tqdm(
            total=min(config.pages, user_profile.tweet_count),
            desc="Get tweet links that meet the requirements",
            leave=False,
            unit="tweet",
        )
        num = 0
        while not (num >= min(config.pages, user_profile.tweet_count)):
            await main_page.evaluate("window.scrollBy(0, 300)")

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
            num += len(_ - pages)
            pages |= _
            await asyncio.sleep(0.5)
        progress.close()
        await main_page.close()
        ordered_url: list[tuple[datetime, str]] = [
            (time, "https://x.com" + link) for time, link in pages
        ]
        ordered_url.sort(key=lambda x: x[0])
        progress = tqdm(
            total=len(ordered_url),
            desc="Extracting information from tweets",
            leave=False,
            unit="tweet",
        )
        semaphore = asyncio.Semaphore(config.thread)

        async def worker(url):
            async with semaphore:
                page = available_page.pop()
                try:
                    return await crawl_tweet(page, url, progress)  # TODO: 实现LLM分析
                finally:
                    available_page.append(page)

        tasks: list = list(
            await asyncio.gather(
                *(worker(_) for _ in ordered_url), return_exceptions=True
            )
        )
        await browser.close()
    for task in tasks:
        if isinstance(task, Exception):
            print(f"{task!r}")
            tasks.remove(task)
    gpt_dict = [
        {"role": "assistant", "content": config.prompt},
        {"role": "user", "content": parse_to_str(list(tasks), user_profile)},
    ]
    stream = await run(gpt_dict)
    async for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="")
    sleep(20)
    print("\n\n")
    print(gpt_dict)


asyncio.run(main())
