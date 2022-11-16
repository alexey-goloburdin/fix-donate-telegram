# @donate Telegram bot addition

You can use [@donate](https://t.me/donate) Telegram bot to create paid Telegram channels available by subscription. And [@donate](https://t.me/donate) will manage the accounts in that channel, but not in linked with channel chat. This small Python script can ban users in chat, who are not in channel now.

To install create new virtual environment and install requirements ([httpx](https://www.python-httpx.org/) and [telethon](https://docs.telethon.dev/en/stable/)).

```bash
python3 -m venv env
source ./env/bin/activate
pip install -r requirements.txt
```

Than create telegram bot with [@BotFather](https://t.me/BotFather). [Documentation](https://core.telegram.org/bots/tutorial) from Telegram. Remember Bot token.

Then [create Telegram app](https://my.telegram.org/), «API development tools» section. Remember `api_id` and `api_hash`.

Then find out your channel id, remember it. You can see it in URL on Telegram web version, for example, [our channel](https://t.me/t0digital) has url `https://web.telegram.org/z/#-1251775798`, so `-1251775798` is our id, but we need add `100` to the start, so we have id: `-1001251775798`.

Add bot as admin to your channel and his linked chat.

Run script with activated virtual environment:

```bash
source ./env/bin/activate

TG_API_ID=... \
    TG_API_HASH=... \
    TG_BOT_TOKEN=... \
    TG_CHANNEL_ID=... \
    python fix-donate-tg-chat.py
```

`TG_API_ID` and `TG_API_HASH` — from [my.telegram.org](https://my.telegram.org). `TG_BOT_TOKEN` from [@BotFather](https://t.me/BotFather). `TG_CHANNEL_ID` is your channel id, `-1001251775798` for [our Telegram channel](https://t.me/t0digital).

You can add this script to cron scheduler for everyday run. For production usage with real ban+unban users uncomment lines in script in `main` function.
