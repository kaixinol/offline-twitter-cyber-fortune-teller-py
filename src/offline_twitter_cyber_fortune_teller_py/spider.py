from .data_type import Profile, Tweet


async def crawl_profile() -> Profile: ...


async def crawl_tweet() -> Tweet: ...
