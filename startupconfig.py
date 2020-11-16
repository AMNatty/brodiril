import json
import typing
import os
import sys


class StartupConfig(object):
    def __init__(self, notify_channel: typing.Optional[int] = None):
        self.notify_channel: typing.Optional[int] = notify_channel


class StartupConfigLoader:
    @staticmethod
    def cache_file() -> str:
        return "./cache/startup_config.json"

    @staticmethod
    def load() -> StartupConfig:
        try:
            file_path = StartupConfigLoader.cache_file()

            if os.path.isfile(file_path):
                print("Restoring startup config from cache...")
                with open(file_path, "r") as file:
                    startup_config = json.load(file)
                    config = StartupConfig(notify_channel=startup_config["notify_channel"])
                os.remove(file_path)
                return config
            else:
                print("No startup config detected.")
        except IOError as e:
            print(e, file=sys.stderr)
        except ValueError as e:
            print(e, file=sys.stderr)
        except KeyError as e:
            print(e, file=sys.stderr)

        return StartupConfig()

    @staticmethod
    def save(config: StartupConfig) -> None:
        file_path = StartupConfigLoader.cache_file()
        with open(file_path, "w") as file:
            json.dump(config.__dict__, file)
