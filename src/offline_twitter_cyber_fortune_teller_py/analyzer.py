import re

import openai
from openai import AsyncOpenAI

from . import config
from .data_type import Tweet, Profile


async def run(msg: dict):
    openai.api_key = config.llm_setting.api_key
    openai.base_url = config.llm_setting.api_server
    client = AsyncOpenAI()
    return client.chat.completions.create(
        model=config.llm_setting.model,
        messages=msg,
        stream=True,
    )


def parse_to_str(tweet: list[Tweet], profile: Profile) -> str:
    def extra_username(_tweet: Tweet) -> str:
        return re.match(config.user_name_regex, _tweet.link).group("name")

    def remove_same_tweet():
        from functools import reduce

        def process_tweets(tweets):
            tweet_map = {hash(t.link): [id(t)] for t in tweets if t.comments is None}
            comment_map = reduce(
                lambda acc, t: acc.update(
                    {
                        hash(c.link): acc.get(hash(c.link), []) + [id(t)]
                        for c in t.comments
                    }
                )
                or acc,
                filter(lambda t: t.comments is not None, tweets),
                {},
            )

            return tweet_map, comment_map

        hash_map, hash_map_comment = process_tweets(tweet)

        handle_items = set(hash_map) & set(hash_map_comment)

        tweet[:] = [
            tw
            for tw in tweet
            if id(tw)
            not in reduce(lambda acc, h: acc + hash_map.get(h, []), handle_items, [])
        ]

        # for h in handle_items:
        #     print(f"removed! {hash_map[h]}")

    remove_same_tweet()
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
                desc += f"\n{retweet.format(name=usr)}\n<{have_image.format(count=(len(i.media) if i.media else 'zero'))}>"
            elif i.text and i.media is None:
                desc += f"\n{retweet.format(name=usr)}:\n{i.text}"
            if i.comments is not None:
                desc += f"\n{have_comment.format(user=profile.username)}:\n{'\n'.join([_.text for _ in i.comments])}"
        else:
            if i.text is None and i.media:
                desc += f"\n<{only_image.format(count=(len(i.media) if i.media else 'zero'))}>"
            elif i.text and i.media:
                desc += f"\n{i.text}\n<{have_image.format(count=(len(i.media) if i.media else 'zero'))}>"
            elif i.text and i.media is None:
                desc += f"\n{i.text}"
            if i.comments is not None:
                desc += f"\n{have_comment.format(user=profile.username)}:\n{'\n'.join([_.text for _ in i.comments])}"

    return desc
