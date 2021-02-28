import os

youtube_api_key = os.getenv("YOUTUBE_API_KEY")
discord_bot_key = os.getenv("DISCORD_API_KEY")
testing_mode = False

print("Discord secret:", discord_bot_key[:6:] + '*' * len(discord_bot_key[6::]))
print("YouTube secret:", youtube_api_key[:3:] + '*' * len(youtube_api_key[3::]))

if not youtube_api_key or not discord_bot_key:
    raise RuntimeError("Missing required secrets.")
