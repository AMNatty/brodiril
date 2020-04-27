#!/bin/bash

BOT_PATH="$(dirname "$0")"

cd $BOT_PATH

python3 -m pip install discord.py
python3 -m pip install beautifulsoup4
python3 -m pip install google-api-python-client

python3 -u bb.py
