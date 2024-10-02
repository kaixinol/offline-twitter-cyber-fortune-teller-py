import re
from datetime import datetime
from random import randint

from offline_twitter_cyber_fortune_teller_py import config
from offline_twitter_cyber_fortune_teller_py.data_type import Tweet, Profile

count = 0


def get_test_data(*, data=None, username: str = None) -> Tweet:
    if data is None:
        data = {}
    global count
    random_year = randint(2019, 2025)
    random_month = randint(1, 12)
    random_day = randint(1, 30)
    random_hour = randint(0, 23)
    random_minute = randint(0, 59)
    random_second = randint(0, 59)
    count += random_year
    return Tweet(
        **(
            dict(
                link=f"https://x.com/{username if username is not None else 'test'}/status/{count}",
                time=datetime(
                    random_year,
                    random_month,
                    random_day,
                    random_hour,
                    random_minute,
                    random_second,
                ),
                text=None,
                media=None,
            )
            | data
        )
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

        for h in handle_items:
            print(f"removed! {hash_map[h]}")

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


test = get_test_data(data={"text": "test1"})
test_tweet = [
    test,
    get_test_data(username="A123", data={"text": "test1"}),
    get_test_data(username="A1", data={"media": ["test"]}),
    get_test_data(
        username="A1",
        data={
            "text": "test2",
            "comments": [test],
        },
    ),
    get_test_data(data={"text": "test3", "media": ["test"]}),
]
