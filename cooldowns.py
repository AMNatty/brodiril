import time
import json
import sys
import datetime

cooldowns: dict = {}

try:
    with open("cooldowns.json") as cooldowns_file:
        cooldowns = json.load(cooldowns_file)
except FileNotFoundError as e:
    print("File does not exist, will be created (eventually): ", e)
except json.JSONDecodeError as e:
    print("JSON decode error!", file=sys.stderr)


def check_cd(user: int, cooldown: str) -> str:
    uk: str = str(user)

    if uk not in cooldowns:
        return None

    if cooldown not in cooldowns[uk]:
        return None

    timediff: float = cooldowns[uk][cooldown] - time.time()

    if timediff < 0:
        return None

    return "{:0>8}".format(str(datetime.timedelta(seconds = int(timediff))))


def update_cd(user: int, cooldown: str, seconds: int) -> None:
    uk: str = str(user)

    if uk not in cooldowns:
        cooldowns[uk]: dict = {}

    cooldowns[uk][cooldown]: float = time.time() + seconds

    with open("cooldowns.json", "w") as cds_file:
        json.dump(cooldowns, cds_file)


def remove_cd(user: int, cooldown: str) -> bool:
    uk: str = str(user)

    if uk not in cooldowns:
        return False

    if cooldown not in cooldowns[uk]:
        return False

    if cooldowns[uk][cooldown] < time.time():
        return False

    del cooldowns[uk][cooldown]

    with open("cooldowns.json", "w") as cds_file:
        json.dump(cooldowns, cds_file)

    return True
