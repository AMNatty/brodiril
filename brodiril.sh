#!/usr/bin/sh
set -e

BOT_PATH="$(dirname "$0")"

cd $BOT_PATH
bro_log_file=$BOT_PATH"/logs/bro_$(date +"%Y-%m-%d-%H-%M-%S").log"

git pull --ff-only >>$bro_log_file 2>&1

static_config_template_file="staticconfig.py.template"
static_config="$(cat "$static_config_template_file")"
git_hash="$(git rev-parse HEAD)"

printf "$static_config\ncommit_hash: str = \"$git_hash\"" > staticconfig.py

python3 -m pip install discord.py  >>$bro_log_file 2>&1
python3 -m pip install beautifulsoup4  >>$bro_log_file 2>&1
python3 -m pip install google-api-python-client  >>$bro_log_file 2>&1

python3 -u bb.py >>$bro_log_file 2>&1 &
BOT_PID="$!"
trap 'kill -9 $BOT_PID' ERR EXIT SIGTERM SIGKILL
wait $BOT_PID
