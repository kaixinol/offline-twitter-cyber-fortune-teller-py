import re
from collections.abc import Callable
from contextlib import suppress
from datetime import datetime
from json import loads
from typing import get_type_hints

from html2text import html2text
from jq import compile
from playwright.async_api import Page, Error
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
import asyncio
from . import xpath, config, inject
from .data_type import Profile, Tweet


async def crawl_profile(page: Page) -> Profile:
    def get_jq_result(expr: str, json: str | dict) -> str:
        if isinstance(json, str):
            json = loads(json)
        return compile(expr).input_value(json).first()

    profile = page.locator(xpath.profile_json.expr)
    json_text = await profile.text_content()
    handler: dict[str, Callable[[str], int | datetime]] = {
        "followed": int,
        "follower": int,
        "tweet_count": int,
        "join_time": lambda x: datetime.fromisoformat(x.rstrip("Z")),
    }
    member = get_type_hints(Profile)
    ret = {}
    for i in member.keys():
        if i not in handler:
            ret[i] = get_jq_result(getattr(xpath.profile_json.jq, i), json_text)
        else:
            ret[i] = handler[i](
                get_jq_result(getattr(xpath.profile_json.jq, i), json_text)
            )
    return Profile(**ret)


async def crawl_tweet(
    page: Page, url_with_time: tuple[datetime, str], progress
) -> Tweet:
    (
        time,
        url,
    ) = url_with_time

    async def get_media() -> list[str] | None:
        with suppress(PlaywrightTimeoutError):
            await frame.locator(xpath.tweet.sensitive_content).first.wait_for(
                state="visible", timeout=config.delay // 10
            )
        try:
            await frame.locator(xpath.tweet.media).first.wait_for(
                state="visible", timeout=config.delay // 10
            )
            tmd = frame.locator(xpath.TMD.button).first
            await tmd.wait_for(state="visible", timeout=config.delay // 10)
            await page.evaluate(xpath.TMD.click)
            while not await frame.evaluate("document.isParsed;"):
                await asyncio.sleep(0.1)
            return await frame.evaluate("document.fileList;")

        except PlaywrightTimeoutError:
            return None

    async def get_text() -> str | None:
        def replace_emoji(string: str) -> str:
            regex = r"!\[(.*?)]\(https://.*\.twimg\.com/emoji/(.*?)\.svg\)"
            if re.search(
                regex,
                string,
                re.MULTILINE,
            ):
                return re.sub(
                    regex,
                    r"\1",
                    string,
                    re.MULTILINE,
                )
            return string

        try:
            await frame.locator(xpath.tweet.text).first.wait_for(
                state="visible", timeout=config.delay // 10
            )
            return (
                replace_emoji(
                    html2text(await page.locator(xpath.tweet.text).inner_text())
                ).strip()
                or None
            )
        except Error:
            return None

    await page.goto(url, wait_until="domcontentloaded")
    await page.evaluate(inject)
    await page.route(
        "**/*",
        lambda route, request: route.abort()
        if request.resource_type in ["image", "media"]
        else route.continue_(),
    )
    frame = page.locator(xpath.tweet.frame)
    await frame.first.wait_for(state="visible", timeout=config.delay)
    ret: dict[str, str | datetime | None] = {}
    progress.update()
    ret["link"] = url
    ret["time"] = time
    ret["text"] = await get_text()
    ret["media"] = await get_media()
    return Tweet(**ret)
