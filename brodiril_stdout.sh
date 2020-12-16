#!/bin/sh
set -e

BOT_PATH="$(dirname "$0")"

cd "$BOT_PATH"

git pull --ff-only

static_config_template_file="staticconfig.py.template"
static_config="$(cat "$static_config_template_file")"
git_hash="$(git rev-parse HEAD)"

printf "%s\ncommit_hash: str = \"%s\"" "$static_config" "$git_hash" > staticconfig.py

python3 -m pip install discord.py
python3 -m pip install beautifulsoup4
python3 -m pip install google-api-python-client

python3 -u bb.py
