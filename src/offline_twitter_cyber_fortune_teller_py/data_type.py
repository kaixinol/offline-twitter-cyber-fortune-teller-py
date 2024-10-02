from datetime import datetime

from pydantic import BaseModel


class JQ(BaseModel):
    nickname: str
    bio: str
    location: str
    following: str
    follower: str
    tweet_count: str
    join_time: str


class Profile(JQ):
    following: int
    follower: int
    tweet_count: int
    join_time: datetime
    username: str


class ProfileJson(BaseModel):
    expr: str
    jq: JQ


class TweetXPath(BaseModel):
    link: str
    media: str
    text: str
    time: str
    frame: str
    sensitive_content: str
    comment: str


class Tweet(BaseModel):
    time: datetime
    media: list[str] | None
    text: str | None
    link: str
    comments: list["Tweet"] | None = None


class TwitterMediaDownloader(BaseModel):
    click: str
    button: str


class XPath(BaseModel):
    tweet: TweetXPath
    profile_json: ProfileJson
    TMD: TwitterMediaDownloader


class LLMSetting(BaseModel):
    api_server: str
    api_key: str
    model: str


class TwitterAnalysisConfig(BaseModel):
    prompt: str
    thread: int | float
    llm_setting: LLMSetting
    pages: int
    delay: int
    user_name_regex: str
