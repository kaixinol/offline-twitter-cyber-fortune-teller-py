import re
from datetime import datetime
from json import loads
from typing import get_type_hints

from html2text import html2text
from jq import compile
from playwright.async_api import Page, Error

from . import xpath, config, inject
from .data_type import Profile, Tweet


async def crawl_profile(page: Page) -> Profile:
    def get_jq_result(expr: str, json: str | dict) -> str:
        if isinstance(json, str):
            json = loads(json)
        return compile(expr).input_value(json).first()

    profile = page.locator(xpath.profile_json.expr)
    json_text = await profile.text_content()
    handler = {
        "followed": lambda x: int(x),
        "follower": lambda x: int(x),
        "tweet_count": lambda x: int(x),
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
        ...
        # TODO: 实现在Tweet里找按钮，找不到返回None，找到了返回list[link: str]

    async def get_text() -> str | None:
        def replace_emoji(string: str) -> str:
            if re.search(
                r"!\[(.*?)]\(https://.*\.twimg\.com/emoji/(.*?)\.svg\)",
                string,
                re.MULTILINE,
            ):
                return re.sub(
                    r"!\[(.*?)]\(https://.*\.twimg\.com/emoji/(.*?)\.svg\)",
                    r"\1",
                    string,
                    re.MULTILINE,
                )
            return string

        try:
            await page.locator(xpath.tweet.text).first.wait_for(
                state="visible", timeout=config.delay
            )
            return (
                replace_emoji(
                    html2text(await page.locator(xpath.tweet.text).inner_text())
                )
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
    ret: dict[str, str | datetime | None] = {}
    progress.update()
    ret["link"] = url
    ret["time"] = time

    return Tweet(**ret)
