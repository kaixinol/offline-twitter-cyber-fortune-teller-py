import re
from collections.abc import Callable
from contextlib import suppress
from datetime import datetime
from functools import wraps
from json import loads
from typing import get_type_hints
from html2text import html2text
from jq import compile
from playwright.async_api import Page, Error
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
import asyncio

from . import xpath, config, inject
from .data_type import Profile, Tweet

__username: str = ""


def exception_add_url(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            url_with_time = kwargs.get("url_with_time") or args[1]
            new_message = f"URL: {url_with_time[1]}\n:{str(e)}"
            raise type(e)(new_message).with_traceback(e.__traceback__)

    return wrapper


async def crawl_profile(page: Page) -> Profile:
    def get_jq_result(expr: str, json: str | dict) -> str:
        if isinstance(json, str):
            json = loads(json)
        return compile(expr).input_value(json).first()

    profile = page.locator(xpath.profile_json.expr)
    json_text = await profile.text_content()
    handler: dict[str, Callable[[str], int | datetime]] = {
        "following": int,
        "follower": int,
        "tweet_count": int,
        "join_time": lambda x: datetime.fromisoformat(x.rstrip("Z")),
    }
    member = get_type_hints(Profile)
    member.pop("username")
    ret = {}
    for i in member.keys():
        _ = get_jq_result(getattr(xpath.profile_json.jq, i), json_text)
        if i not in handler:
            ret[i] = _
        else:
            ret[i] = handler[i](_)
        if ret[i] is None:
            ret[i] = "unknown"
    ret["username"] = re.search(config.user_name_regex, page.url).group("name")
    global __username
    __username = ret["username"]
    return Profile(**ret)


@exception_add_url
async def crawl_tweet(
    page: Page, url_with_time: tuple[datetime, str], progress
) -> Tweet | list[Tweet]:
    (
        time,
        url,
    ) = url_with_time

    async def get_comment() -> list[Tweet] | None:
        comment = await page.locator(xpath.tweet.comment.format(name=__username)).all()
        if len(comment) in (0, 1):
            return
        return [
            Tweet(
                link="https://x.com"
                + await _.locator(xpath.tweet.link).get_attribute("href"),
                time=datetime.fromisoformat(
                    (
                        await _.locator(xpath.tweet.link)
                        .locator("time")
                        .get_attribute("datetime")
                    ).rstrip("Z")
                ),
                text=await _.locator(xpath.tweet.text).inner_text(),
                media=None,
            )
            for _ in comment
        ]

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
        def replace_emoji(string: str) -> str:  # TODO: fix emoji missing bug
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
                    html2text(await page.locator(xpath.tweet.text).first.inner_text())
                ).strip()
                or None
            )
        except Error:
            return None

    async def get_fallback_text() -> str:
        def find_nth_occurrence(
            string: str, substring: str, n: int, from_right: bool = False
        ) -> int:
            """
            Function to find the position of the nth occurrence of a substring
            Also supports searching from the right and returns the count starting from the right
            """
            if from_right:
                reverse_index = len(string)
                for _ in range(n):
                    reverse_index = string.rfind(substring, 0, reverse_index)
                    if reverse_index == -1:
                        return -1
                return reverse_index
            else:
                index = -1
                for _ in range(n):
                    index = string.find(substring, index + 1)
                    if index == -1:
                        return -1
                return index

        _tmp = html2text(await frame.inner_html())
        return _tmp[
            find_nth_occurrence(_tmp, "\n\n", 4) : find_nth_occurrence(
                _tmp, "\n\n", 8, from_right=True
            )
        ].replace("\n\n", "\n")

    await page.goto(url, wait_until="domcontentloaded")
    await page.evaluate(inject)
    await page.route(
        "**/*",
        lambda route, request: route.abort()
        if request.resource_type in ["image", "media"]
        else route.continue_(),
    )
    frame = page.locator(
        xpath.tweet.frame.format(tweet_id=re.search(r"(\d+)(?!.*\d)", url).group())
    )
    await frame.first.wait_for(state="visible", timeout=config.delay)
    progress.update()
    comments: list[Tweet] | None = None
    try:
        comments = await get_comment()
    except PlaywrightTimeoutError:
        pass
    try:
        data = {
            "text": await get_text(),
            "media": await asyncio.wait_for(get_media(), timeout=5),
        }
    except asyncio.TimeoutError:
        text = await get_fallback_text()
        data = {"text": text, "media": None}
    if comments is None:
        return Tweet(link=url, time=time, **data)
    return Tweet(
        link=url,
        time=time,
        **data,
        comments=comments,
    )
