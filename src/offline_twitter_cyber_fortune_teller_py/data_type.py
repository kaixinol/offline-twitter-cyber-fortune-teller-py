from pydantic import BaseModel


class JQ(BaseModel):
    nickname: str
    bio: str
    location: str
    followed: str
    follower: str
    tweet_count: str


class ProfileJson(BaseModel):
    expr: str
    jq: JQ


class Tweet(BaseModel):
    link: str
    media: str
    text: str
    time: str


class XPath(BaseModel):
    birthday_var: str
    tweet: Tweet
    profile_json: ProfileJson


class LLMSetting(BaseModel):
    type: str
    api_server: str = "DEFAULT"
    api_key: str


class TwitterAnalysisConfig(BaseModel):
    prompt: str
    thread: int
    llm_api_slow_mode: bool
    twitter_access_slow_mode: bool
    llm_setting: LLMSetting
