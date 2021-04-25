import typing

bot_id: int = 565299046613516288
manager: int = 263648016982867969


class Vandiland:
    logging_channel:        int = 471357087763529729
    gid:                    int = 220920607099846657
    uploaded_channel_id:    int = 498415887179841567
    emoji_kekban:           int = 695214550517153792
    bug_administrator:      int = 500694663745896458
    bug_notifications_role: int = 702665168794157077
    forums_channel_id:      int = 485434667982651392


class Coding:
    id:                     int = 747545877018706061
    tech_news_videos_id:    int = 747549969816223844
    important_videos_id:    int = 791032028430729237
    other_id:               int = 832770801014669342


class Johann:
    uploaded_channel_id:    int = 822525060677238844
    announcements_role:     int = 831919915811209276


class YTChannel:
    def __init__(self, channel_name: str,
                 target_channel: int,
                 playlist_id: str,
                 should_ping: bool = False,
                 ping_role: typing.Optional[int] = None):
        self.name: str = channel_name
        self.target_channel: int = target_channel
        self.playlist_id: str = playlist_id
        self.should_ping: bool = should_ping
        self.ping_role: typing.Optional[int] = ping_role


channel_list: typing.List[YTChannel] = [
    YTChannel("Vandiril", Vandiland.uploaded_channel_id, "UUZ-oWkpMnHjTJpeOOlD80OA", should_ping=True),
    YTChannel("Gamediril", Vandiland.uploaded_channel_id, "UUXempLARIyhl6dM2yg1sw4A"),

    YTChannel("TechLinked", Coding.tech_news_videos_id, "UUeeFfhMcJa1kjtfZAGskOCA"),
    YTChannel("Hardware Unboxed", Coding.tech_news_videos_id, "UUI8iQa1hv7oV_Z8D35vVuSg"),
    YTChannel("Linus Tech Tips", Coding.tech_news_videos_id, "UUXuqSBlHAE6Xw-yeJA0Tunw"),
    YTChannel("Gamers Nexus", Coding.tech_news_videos_id, "UUhIs72whgZI9w6d6FhwGGHA"),
    YTChannel("Techquickie", Coding.tech_news_videos_id, "UU0vBXGSyV14uvJ4hECDOl0Q"),

    YTChannel("Tom Scott", Coding.important_videos_id, "UUBa659QWEk1AI4Tg--mrJ2A"),
    YTChannel("Half as Interesting", Coding.important_videos_id, "UUuCkxoKLYO_EQ2GeFtbM_bw"),
    YTChannel("Wendover Productions", Coding.important_videos_id, "UU9RM-iSvTu1uPJb8X5yp3EQ"),

    YTChannel("LiveOverflow", Coding.other_id, "UUlcE-kVhqyiHCcjYwcpfj9w"),
    YTChannel("Sebastian Lague", Coding.other_id, "UUmtyQOKKmrMVaKuRXz02jbQ"),

    YTChannel("Jóhann", Johann.uploaded_channel_id, "UUkNNlzB4Squ2n9iaDTt3Igw", should_ping=True, ping_role=Johann.announcements_role),
]


SECOND: int = 1
MINUTE: int = SECOND * 60
HOUR:   int = MINUTE * 60
DAY:    int = HOUR * 24


rename_cooldown: int = 30 * DAY


# The period between API calls / data refreshes
delay_refresh: int = 240

try:
    from dulwich import repo
    current_repo = repo.Repo(".")
    commit_hash: str = current_repo.head().decode("ASCII")
except ModuleNotFoundError:
    commit_hash: str = "???"
except repo.NotGitRepository:
    commit_hash: str = "???"

if __name__ == "__main__":
    print("Current commit hash: ", commit_hash)
