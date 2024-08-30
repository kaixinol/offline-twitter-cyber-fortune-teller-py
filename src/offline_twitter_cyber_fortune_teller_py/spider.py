from collections.abc import Callable
from datetime import datetime
from json import loads
from typing import get_type_hints, Awaitable

from jq import compile
from playwright.async_api import Page, Error

from . import xpath
from .data_type import Profile, Tweet
from .lock import update


async def crawl_profile(page: Page) -> Profile:
    def get_data(expr: str, json: str | dict) -> str:
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
            ret[i] = get_data(getattr(xpath.profile_json.jq, i), json_text)
        else:
            ret[i] = handler[i](get_data(getattr(xpath.profile_json.jq, i), json_text))
    return Profile(**ret)


async def crawl_tweet(
    page: Callable[[], Awaitable[Page]], url_with_time: tuple[datetime, str], progress
) -> Tweet:
    (
        time,
        url,
    ) = url_with_time
    print(f"{url} 尝试获取page()")
    page = await page()
    print(f"{id(page)}获取成功")
    await page.goto(url)
    await page.route(
        "**/*",
        lambda route, request: route.abort()
        if request.resource_type in ["image", "media"]
        else route.continue_(),
    )
    print(f"{id(page)}访问成功")

    ret: dict[str, object] = {}
    try:
        await page.locator(xpath.tweet.text).first.wait_for(
            state="visible", timeout=50000
        )
        ret["text"] = await page.locator(xpath.tweet.text).inner_text()
    except Error:
        ret["text"] = None
    print(f"{id(page)} {ret['text']}获取成功")
    try:
        ret["media"] = await page.locator(xpath.tweet.media).first.wait_for(
            state="visible", timeout=50000
        )
    except Error:
        ret["media"] = None
    print(f"{id(page)} {ret['media']}获取成功")
    await update({id(page): False})
    print(f"{id(page)} 解锁成功")
    progress.update()
