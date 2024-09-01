from datetime import datetime

from pydantic import BaseModel


class JQ(BaseModel):
    nickname: str
    bio: str
    location: str
    followed: str
    follower: str
    tweet_count: str
    join_time: str


class Profile(JQ):
    followed: int
    follower: int
    tweet_count: int
    join_time: datetime


class ProfileJson(BaseModel):
    expr: str
    jq: JQ


class TweetXPath(BaseModel):
    link: str
    media: str | None
    text: str | None
    time: str


class Tweet(TweetXPath):
    time: datetime


class XPath(BaseModel):
    tweet: TweetXPath
    profile_json: ProfileJson


class LLMSetting(BaseModel):
    api_server: str = "DEFAULT"
    api_key: str


class TwitterAnalysisConfig(BaseModel):
    prompt: str
    thread: int | float
    llm_api_slow_mode: bool
    twitter_access_slow_mode: bool
    llm_setting: LLMSetting
    pages: int
    delay: int
