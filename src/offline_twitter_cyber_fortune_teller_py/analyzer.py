import re

from openai import AsyncOpenAI

from . import config
from .data_type import Tweet, Profile


async def run(msg: list):
    if config.llm_setting.api_server != "DEFAULT":
        base_url = config.llm_setting.api_server
    else:
        base_url = None
    client = AsyncOpenAI(api_key=config.llm_setting.api_key, base_url=base_url)
    return await client.chat.completions.create(
        model=config.llm_setting.model,
        messages=msg,
        stream=True,
    )


def parse_to_str(tweet: list[Tweet], profile: Profile) -> str:
    def extra_username(_tweet: Tweet) -> str:
        return re.match(config.user_name_regex, _tweet.link).group("name")

    have_image = "This tweet also contains {count} media"
    only_image = "This tweet contains only {count} media and no text"
    retweet = "This user retweeted {name}'s tweet"
    have_comment = "The tweet also included the following comment from {user}"
    user_desc = """
This user's nickname is: {nickname}, 
joining time is: {join_time}, 
username is: {username},
bio is: {bio}, 
location is: {location},
count of tweets is: {tweet_count},
number of followers is: {follower},
number of following is: {following}
""".strip()
    desc = user_desc.format(**profile.model_dump())
    for i in tweet:
        desc += "\n" + "-" * 5
        usr = extra_username(i)
        desc += "\nPost Date:" + str(i.time)
        if usr != profile.username:
            if i.text is None and i.media:
                desc += f"\n{retweet.format(name=usr)}:\n<{only_image.format(count=(len(i.media) if i.media else 'zero'))}>"
            elif i.text and i.media:
                desc += f"\n{retweet.format(name=usr)}\n{i.text}\n<{have_image.format(count=(len(i.media) if i.media else 'zero'))}>"
            elif i.text and i.media is None:
                desc += f"\n{retweet.format(name=usr)}:\n{i.text}"
            if i.comments:
                desc += f"\n{have_comment.format(user=profile.username)}:\n{'\n'.join([_.text for _ in i.comments if _.text != i.text])}"
        else:
            if i.text is None and i.media:
                desc += f"\n<{only_image.format(count=(len(i.media) if i.media else 'zero'))}>"
            elif i.text and i.media:
                desc += f"\n{i.text}\n<{have_image.format(count=(len(i.media) if i.media else 'zero'))}>"
            elif i.text and i.media is None:
                desc += f"\n{i.text}"
            if i.comments:
                desc += f"\n{have_comment.format(user=profile.username)}:\n{'\n'.join([_.text for _ in i.comments if _.text != i.text])}"

    return desc
