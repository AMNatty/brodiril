#!/bin/sh
set -e

if ! [ -x "$(command -v git)" ]; then
    echo "Git must be installed in order to run this script!"
    exit 1
fi

BOT_PATH="$(dirname "$0")"

cd "$BOT_PATH"
bro_log_file=$BOT_PATH"/logs/bro_$(date +"%Y-%m-%d-%H-%M-%S").log"

git pull --ff-only >>"$bro_log_file" 2>&1

python3 -m pip install -r requirements.txt  >>"$bro_log_file" 2>&1

python3 -u bb.py >>"$bro_log_file" 2>&1 &
BOT_PID="$!"
trap 'kill -9 $BOT_PID' EXIT TERM
wait $BOT_PID
