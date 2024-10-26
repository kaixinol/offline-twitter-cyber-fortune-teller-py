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
print(
    parse_to_str(
        test_tweet,
        Profile(
            username="test",
            nickname="tt",
            bio="test",
            location="hell",
            following=12,
            follower=20,
            tweet_count=20,
            join_time=datetime(1, 2, 3),
        ),
    )
)
a = [
    Tweet(
        time=datetime.datetime(2024, 1, 29, 23, 17, 51),
        media=["https://pbs.twimg.com/media/GFC9pB6boAAwq3y.jpg:orig"],
        text="The story of computing is the story of humanity: this is a story of ambition,\ninvention, creativity, vision, avarice, power, and serendipity, powered by a\nrefusal to accept the limits of our bodies and our minds.",
        link="https://x.com/Grady_Booch/status/1752108825954680867",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 5, 5, 14, 40),
        media=[
            "https://video.twimg.com/ext_tw_video/1787023571094810624/pu/vid/avc1/720x720/vvoQgoPzArBghZnL.mp4?tag=12"
        ],
        text="The Sun unleashing a spectacular solar flare and coronal mass ejection,\ncaptured by the Solar Dynamics Observatory spacecraft.",
        link="https://x.com/wonderofscience/status/1787130126984982650",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 5, 6, 2, 9, 3),
        media=None,
        text="1b txn",
        link="https://x.com/jack/status/1787303532565049408",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 5, 6, 3, 47, 41),
        media=["https://pbs.twimg.com/media/GM3BpLEWwAAG5Cy.jpg:orig"],
        text="settles that",
        link="https://x.com/jack/status/1787328354112156139",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 5, 6, 19, 26, 53),
        media=["https://pbs.twimg.com/media/GM1mrTuXQAAmvLQ.jpg:orig"],
        text="As bad as this chart looks, it somehow still feels like an underestimate.",
        link="https://x.com/Snowden/status/1787564713200517460",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 5, 6, 20, 33, 34),
        media=["https://pbs.twimg.com/media/GM7D5KwXYAEVKN-.jpg:orig"],
        text="Throwback to one of the hardest fits ever worn #MetGala",
        link="https://x.com/vidsthatgohard/status/1787581493990113693",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 5, 7, 17, 22, 23),
        media=None,
        text="did not know this",
        link="https://x.com/jack/status/1787895769183268948",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 5, 7, 21, 32, 30),
        media=None,
        text="Hi, hello, we don’t have evidence of extant vulnerabilities, and haven’t been\nnotified of anything. We follow responsible disclosure practices, and closely\nmonitor security@signal.org + respond & fix any valid issues quickly. So if\nyou do have more info hit us up! But beyond this... ...we’ve put a lot of\nthought into making sure our structure and development practices let people\nvalidate our claims, instead of just taking our word for it. This is\nparticularly important to me, since I saw the view from inside a massive tech\nco and observed how widely their claims could diverge from reality when\nopenness, validation, and an actual commitment to principles were not\nprioritized. Unlike almost all tech orgs we also build with the belief that\nthe only way to keep data safe is not to collect it in the first place. You\ncan see this in action when you clock the vanishingly small amount of data we\nhave been able to turn over when forced. We fight all subpoenas, and when we\nare forced to hand anything over, we fight to unseal them and post them here:\nhttps://signal.org/bigbrother/ I’ve provided some links below so you can go\ndeeper. In brief: \\-- We use cryptography to keep data out of the hands of\neveryone but those it’s meant for (this includes protecting it from us). The\nSignal Protocol is the gold standard in the industry for a reason–it’s been\nhammered and attacked for over a decade, and it continues to stand the test of\ntime. \\-- We engage in regular professional audits (last one completed late\nJan 2024). \\-- We develop in the open, and leverage reproducible builds. A\nlarge community of infosec researchers closely scrutinizes every single\nupdate, combing through our repos and binaries. This means that any nefarious\nchange that affects the security of the Signal Protocol, of our codebase, or\nof the binaries we ship, would be detected almost immediately even on\nplatforms like iOS where reproducible builds are not currently possible (BTW,\nplease pressure Apple to make them possible). This is like an immune system\nprotecting Signal from malign forces–wherever they may be–and ensuring the\nsafety of the millions and millions of people who rely on Signal for sensitive\ncommunications. (We’re really grateful that so many people care enough about\nprivacy to dedicate time and energy to ensuring Signal’s robustness.) \\--\nFinally, we’re also a nonprofit, which means we have no incentive to hype\nbullshit in order to get acquired or bought out–because even if someone did\nbuy Signal, per the 501c3 tax code the money would need to be reinvested in a\nmission-aligned cause. https://github.com/signalapp/ https://signal.org/docs/\nhttps://signal.org/blog/reproducible-android/… https://signal.org/blog/signal-\nfoundation/…",
        link="https://x.com/mer__edith/status/1787958712595784166",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 5, 8, 10, 54, 55),
        media=["https://pbs.twimg.com/media/GNDSoUDXIAAOpSU.jpg:orig"],
        text=None,
        link="https://x.com/MassiveAttackUK/status/1788160645755523472",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 5, 10, 20, 48, 12),
        media=[
            "https://pbs.twimg.com/media/GNPtmX-XoAAb6lT.jpg:orig",
            "https://pbs.twimg.com/media/GNPtmX4XIAAlEiJ.jpg:orig",
            "https://pbs.twimg.com/media/GNPtmXPWYAAkK0q.jpg:orig",
            "https://pbs.twimg.com/media/GNPtmYBWsAA3OuQ.jpg:orig",
        ],
        text="JUST IN - Aurora spotted over Russia, Ukraine, Germany, Slovenia, Australia\nand New Zealand etc due to intense solar storm",
        link="https://x.com/TheInsiderPaper/status/1789034728336523459",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 5, 11, 21, 15, 21),
        media=["https://pbs.twimg.com/media/GNU0uk9bQAAdQPU.jpg:orig"],
        text="fact",
        link="https://x.com/jack/status/1789403948861829604",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 5, 11, 23, 52, 9),
        media=None,
        text="i choose me",
        link="https://x.com/jack/status/1789443409029042589",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 5, 18, 20, 39, 16),
        media=None,
        text='It seems to me that before "urgently figuring out how to control AI systems\nmuch smarter than us" we need to have the beginning of a hint of a design for\na system smarter than a house cat. Such a sense of urgency reveals an\nextremely distorted view of reality. No wonder the more',
        link="https://x.com/ylecun/status/1791931584360206523",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 5, 22, 13, 31, 5),
        media=None,
        text="[](/lopp)\n\n[Jameson Lopp](/lopp)\n\n[@lopp](/lopp)\n\n订阅\n\n点击 订阅 到 lopp\n\nA perfect source of entropy has never been inv...\n\n翻译帖子\n\n引用\n\nvx-underground\n\n@vxunderground\n\n·\n\n5月22日\n\n无法播放该媒体。\n\n重新载入\n\n[下午9:31 · 2024年5月22日](/lopp/status/1793273378448580839)\n\n·\n\n68.8万\n\n查看\n\n117\n\n365\n\n2,771\n\n346\n\n",
        link="https://x.com/lopp/status/1793273378448580839",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 5, 22, 17, 3, 47),
        media=["https://pbs.twimg.com/media/GOMejx2XAAAadwv.jpg:orig"],
        text="If you are a student interested in building the next generation of AI systems,\ndon't work on LLMs",
        link="https://x.com/ylecun/status/1793326904692428907",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 6, 1, 23, 48, 51),
        media=None,
        text='Julian Assange is locked in a dungeon as a political prisoner for the "crime"\nof publishing award-winning stories nearly fifteen years ago, and yet there\nare people on here claiming that we have a justice system.',
        link="https://x.com/Snowden/status/1797052722371301783",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 6, 4, 12, 23, 30),
        media=None,
        text="#FreeToomaj\u200c",
        link="https://x.com/jack/status/1797967412027101207",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 6, 4, 12, 23, 30),
        media=None,
        text="[](/lopp)\n\n[Jameson Lopp](/lopp)\n\n[@lopp](/lopp)\n\n订阅\n\n点击 订阅 到 lopp\n\nA perfect source of entropy has never been inv...\n\n翻译帖子\n\n引用\n\nvx-underground\n\n@vxunderground\n\n·\n\n5月22日\n\n[下午9:31 · 2024年5月22日](/lopp/status/1793273378448580839)\n\n·\n\n68.8万\n\n查看\n\n117\n\n365\n\n2,771\n\n346\n\n",
        link="https://x.com/lopp/status/1793273378448580839",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 7, 10, 21, 27, 4),
        media=[
            "https://video.twimg.com/ext_tw_video/1811150138754134016/pu/vid/avc1/720x982/xZ4ERNyDEf_QeLr_.mp4?tag=12"
        ],
        text="never give up",
        link="https://x.com/bellucciax/status/1811150170744037528",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 7, 11, 18, 27),
        media=None,
        text="The #Bitcoin miner project and 15 EH/s ASIC order announced by @blocks\nyesterday gives $CORZ the ability to reduce future costs and gain even more\ncontrol over our mining operations. Learn more about our relationship here:",
        link="https://x.com/Core_Scientific/status/1811467240467726471",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 7, 19, 20, 9, 37),
        media=None,
        text="A single point of truth is a single point of failure.",
        link="https://x.com/balajis/status/1814392170247532601",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 7, 20, 23, 38, 36),
        media=None,
        text="Journalism is not a crime. I will continue to stand strong for press freedom\nin Russia and worldwide, and stand against all those who seek to attack the\npress or target journalists.",
        link="https://x.com/Stella_Assange/status/1814807148083495247",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 7, 24, 7, 33, 40),
        media=["https://pbs.twimg.com/media/GTPG_MZXgAAiIkX.jpg:orig"],
        text="Strong picture!",
        link="https://x.com/Thom_Wolf/status/1816013867752865938",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 7, 24, 9, 35, 50),
        media=None,
        text="this is the way",
        link="https://x.com/jack/status/1816044610025660666",
        comments=[
            Tweet(
                time=datetime.datetime(2024, 7, 24, 9, 35, 50),
                media=None,
                text="this is the way",
                link="https://x.com/jack/status/1816044610025660666",
                comments=None,
            ),
            Tweet(
                time=datetime.datetime(2024, 7, 24, 9, 35, 50),
                media=None,
                text="nor do i care. open source and open protocols don't require trusting anyone but yourself.",
                link="https://x.com/jack/status/1816044610025660666",
                comments=None,
            ),
        ],
    ),
    Tweet(
        time=datetime.datetime(2024, 7, 24, 12, 37, 4),
        media=["https://pbs.twimg.com/media/GTQMZagXYAAfmjN.jpg:orig"],
        text="Today we're launching @ProtonWallet , an open-source, E2E-encrypted, and self-\ncustodial #Bitcoin wallet. With features like Bitcoin via Email, we hope to be\na safer and easier way for Bitcoin newcomers to get started. Learn more and\nget early access: http://proton.me/wallet",
        link="https://x.com/ProtonWallet/status/1816090220359475651",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 8, 14, 11, 0, 39),
        media=None,
        text="https://ohmni.com/product-detail/tin-foil-hat…",
        link="https://x.com/jack/status/1823676100167299125",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 8, 28, 18, 55, 33),
        media=None,
        text="We're far more interested in a chess match between grandmasters than between\nAIs, even though the AIs are way better. I'm noticing the same thing with\nvideo and art. Once I realize it's made by AI I lose interest, no matter how\ngood it is. Maybe a good sign for human creators?",
        link="https://x.com/waitbutwhy/status/1828869042196672597",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 9, 1, 17, 53, 34),
        media=None,
        text="[](/jack)\n\n[jack](/jack)\n\n[@jack](/jack)\n\n[](https://t.co/jc2w0bH9Pb)\n\n[mullvad.netMullvad VPN - Free the internetFree the internet from mass\nsurveillance and censorship. Fight for privacy with Mullvad VPN and Mullvad\nBrowser.](https://t.co/jc2w0bH9Pb)\n\n[上午1:53 · 2024年9月2日](/jack/status/1830302995101413566)\n\n·\n\n473.7万\n\n查看\n\n621\n\n2,380\n\n1.6万\n\n1万\n\n",
        link="https://x.com/jack/status/1830302995101413566",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 9, 5, 8, 29, 18),
        media=None,
        text="yes",
        link="https://x.com/jack/status/1831610547126636940",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 9, 6, 11, 54, 10),
        media=None,
        text=None,
        link="https://x.com/jack/status/1832024488889745827",
        comments=[
            Tweet(
                time=datetime.datetime(2024, 9, 6, 11, 54, 10),
                media=None,
                text="Jack already knows about nostr, so this, plus his bg in granting government control over our speech, is telling me he might still be compromised. Why divert us from nostr \n@jack\n ??????",
                link="https://x.com/jack/status/1832024488889745827",
                comments=None,
            ),
            Tweet(
                time=datetime.datetime(2024, 9, 6, 11, 54, 10),
                media=None,
                text="@jack\n  \n@OpenChat",
                link="https://x.com/jack/status/1832024488889745827",
                comments=None,
            ),
        ],
    ),
    Tweet(
        time=datetime.datetime(2024, 9, 6, 12, 32, 12),
        media=None,
        text=None,
        link="https://x.com/jack/status/1832034062501896254",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 9, 6, 12, 32, 12),
        media=None,
        text=None,
        link="https://x.com/jack/status/1832024488889745827",
        comments=[
            Tweet(
                time=datetime.datetime(2024, 9, 6, 11, 54, 10),
                media=None,
                text="Jack already knows about nostr, so this, plus his bg in granting government control over our speech, is telling me he might still be compromised. Why divert us from nostr \n@jack\n ??????",
                link="https://x.com/jack/status/1832024488889745827",
                comments=None,
            ),
            Tweet(
                time=datetime.datetime(2024, 9, 6, 11, 54, 10),
                media=None,
                text="@jack\n  \n@OpenChat",
                link="https://x.com/jack/status/1832024488889745827",
                comments=None,
            ),
        ],
    ),
    Tweet(
        time=datetime.datetime(2024, 9, 6, 12, 35, 5),
        media=None,
        text="[](/mullvadnet)\n\n[Mullvad.net](/mullvadnet)\n\n[@mullvadnet](/mullvadnet)\n\nDefense against AI-guided Traffic Analysis (DAITA) Now available on Linux and\nmacOS\n\n[](https://t.co/wmvp2vDM8X)\n\n[来自 mullvad.net](https://t.co/wmvp2vDM8X)\n\n[下午8:35 · 2024年9月6日](/mullvadnet/status/1832034789135630532)\n\n·\n\n15.8万\n\n查看\n\n28\n\n142\n\n668\n\n172\n\n",
        link="https://x.com/mullvadnet/status/1832034789135630532",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 9, 8, 10, 12, 44),
        media=None,
        text="[](/jack)\n\n[jack](/jack)\n\n[@jack](/jack)\n\n[](https://t.co/0vvAOLT0mu)\n\n[alphaxiv.orgalphaXivComment directly on top of arXiv\npapers.](https://t.co/0vvAOLT0mu)\n\n[下午6:12 · 2024年9月8日](/jack/status/1832723738908819926)\n\n·\n\n34.4万\n\n查看\n\n107\n\n349\n\n2,118\n\n995\n\n",
        link="https://x.com/jack/status/1832723738908819926",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 9, 11, 19, 30, 58),
        media=None,
        text="I’m moving $1B of my Square equity (~28% of my wealth) to #startsmall LLC to\nfund global COVID-19 relief. After we disarm this pandemic, the focus will\nshift to girl’s health and education, and UBI. It will operate transparently,\nall flows tracked here:",
        link="https://x.com/jack/status/1833951387153293545",
        comments=[
            Tweet(
                time=datetime.datetime(2020, 4, 7, 20, 4, 19),
                media=None,
                text="I’m moving $1B of my Square equity (~28% of my wealth) to #startsmall LLC to fund global COVID-19 relief. After we disarm this pandemic, the focus will shift to girl’s health and education, and UBI. It will operate transparently, all flows tracked here:",
                link="https://x.com/jack/status/1247616214769086465",
                comments=None,
            ),
            Tweet(
                time=datetime.datetime(2020, 4, 7, 20, 4, 19),
                media=None,
                text="here's the new #startsmall tracker (the original got locked). all past and future grants recorded here. free and open source software support has been added to the focus.",
                link="https://x.com/jack/status/1247616214769086465",
                comments=None,
            ),
            Tweet(
                time=datetime.datetime(2020, 4, 7, 20, 4, 19),
                media=None,
                text="§109  \n@jack",
                link="https://x.com/jack/status/1247616214769086465",
                comments=None,
            ),
        ],
    ),
    Tweet(
        time=datetime.datetime(2024, 9, 11, 19, 31, 57),
        media=None,
        text="We reject: kings, presidents, and voting. We believe in: rough consensus and\nrunning code. —David Clark, 1992",
        link="https://x.com/jack/status/1833951636005552366",
        comments=None,
    ),
    Tweet(
        time=datetime.datetime(2024, 9, 11, 19, 31, 57),
        media=None,
        text="I’m moving $1B of my Square equity (~28% of my wealth) to #startsmall LLC to\nfund global COVID-19 relief. After we disarm this pandemic, the focus will\nshift to girl’s health and education, and UBI. It will operate transparently,\nall flows tracked here:",
        link="https://x.com/jack/status/1833951387153293545",
        comments=[
            Tweet(
                time=datetime.datetime(2020, 4, 7, 20, 4, 19),
                media=None,
                text="I’m moving $1B of my Square equity (~28% of my wealth) to #startsmall LLC to fund global COVID-19 relief. After we disarm this pandemic, the focus will shift to girl’s health and education, and UBI. It will operate transparently, all flows tracked here:",
                link="https://x.com/jack/status/1247616214769086465",
                comments=None,
            ),
            Tweet(
                time=datetime.datetime(2020, 4, 7, 20, 4, 19),
                media=None,
                text="here's the new #startsmall tracker (the original got locked). all past and future grants recorded here. free and open source software support has been added to the focus.",
                link="https://x.com/jack/status/1247616214769086465",
                comments=None,
            ),
            Tweet(
                time=datetime.datetime(2020, 4, 7, 20, 4, 19),
                media=None,
                text="§109  \n@jack",
                link="https://x.com/jack/status/1247616214769086465",
                comments=None,
            ),
        ],
    ),
]
