from datetime import datetime
from json import loads
from typing import get_type_hints

from jq import compile
from playwright.async_api import Page

from . import xpath
from .data_type import Profile, Tweet


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


async def crawl_tweet() -> Tweet: ...
