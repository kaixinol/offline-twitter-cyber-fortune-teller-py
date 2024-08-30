from datetime import datetime
from json import loads
from typing import get_type_hints

from jq import compile
from playwright.async_api import Page, Error

from . import xpath, config
from .data_type import Profile, Tweet


class TweetData(Tweet):
    time: datetime


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
    page: Page, url_with_time: tuple[datetime, str], progress
) -> TweetData:
    (
        time,
        url,
    ) = url_with_time
    await page.goto(url, wait_until="domcontentloaded")
    await page.route(
        "**/*",
        lambda route, request: route.abort()
        if request.resource_type in ["image", "media"]
        else route.continue_(),
    )
    ret: dict[str, object] = {}
    try:
        await page.locator(xpath.tweet.text).first.wait_for(
            state="visible", timeout=config.delay
        )
        ret["text"] = await page.locator(xpath.tweet.text).inner_text()
    except Error:
        ret["text"] = None
    try:
        ret["media"] = await page.locator(xpath.tweet.media).first.wait_for(
            state="visible", timeout=config.delay
        )
    except Error:
        ret["media"] = None
    progress.update()
    ret["link"] = url
    ret["time"] = time

    return TweetData(**ret)
