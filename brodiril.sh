#!/bin/bash

BOT_PATH="$(dirname "$0")"

cd $BOT_PATH

bro_log_file=$BOT_PATH"/logs/bro_$(date -d "today" +"%Y-%m-%d-%H-%M-%S").log"

python3 -m pip install discord.py  >>$bro_log_file 2>&1
python3 -m pip install beautifulsoup4  >>$bro_log_file 2>&1
python3 -m pip install google-api-python-client  >>$bro_log_file 2>&1

python3 -u bb.py >>$bro_log_file 2>&1
