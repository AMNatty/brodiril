#!/bin/sh
set -e

BOT_PATH="$(dirname "$0")"

cd "$BOT_PATH"

git pull --ff-only

python3 -m pip install -r requirements.txt

python3 -u bb.py
