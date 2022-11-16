"""
Removes from Telegram channel's chat users that in chat but not in channel.
Can use with @donate subscription channels.
"""
import logging
import os
import time
import urllib.parse

import httpx
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import User


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


try:
    # api_id and api_hash from my.telegram.org, «API development tools» section
    TG_API_ID = int(os.environ["TG_API_ID"])
    TG_API_HASH = os.environ["TG_API_HASH"]
    # bot_token from Telegram's @BotFather
    TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
    # Id of your telegram channel. You can see it in web.telegram.org/z/,
    # add -100 to the string start.
    # For example, id in URL is 123, so use -100123 here
    TG_CHANNEL_ID = int(os.environ["TG_CHANNEL_ID"])
    logger.debug("Env variables loaded")
    logger.debug(f"Work with channel_id {TG_CHANNEL_ID}")
except (KeyError, ValueError):
    logger.critical(
        "Please, set correct env variables: \n"
        "  * TG_API_ID\n  * TG_API_HASH\n  * TG_BOT_TOKEN\n  * TG_CHANNEL_ID")
    raise


def get_tg_url(method: str, **params) -> str:
    """Returns URL for Telegram Bot API method `method`
    and optional key=value `params`"""
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/{method}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    return url


def get_telegram_chat_id_by_channel_id(channel_id: int) -> int:
    """Returns chat id for channel's linked chat"""
    url = get_tg_url(method="getChat", chat_id=channel_id)
    json_response  = httpx.get(url).json()
    return json_response["result"]["linked_chat_id"]


def is_user_in_channel(user_id: int, channel_id: int) -> bool:
    """Returns True if user `user_id` in `channel_id` now"""
    url = get_tg_url(method="getChatMember",
            chat_id=channel_id, user_id=user_id)
    json_response  = httpx.get(url).json()
    try:
        return json_response["result"]["status"] in (
            "member", "creator", "administrator"
        )
    except KeyError:
        return False


def get_all_chat_users(chat_id: int) -> list[User]:
    """Returns list of all chat users by `chat_id`"""
    logger.debug(f"Load users for chat {chat_id}")
    client = TelegramClient('bot', TG_API_ID, TG_API_HASH)\
            .start(bot_token=TG_BOT_TOKEN)
    all_users = []
    with client:
        chat = client.get_entity(chat_id)
        limit = 100
        index = 0
        while True:
            users = client(GetParticipantsRequest(
                chat, filter=chat,  # type: ignore
                offset=index * limit, limit=limit, hash=0)
            ).users  # type: ignore
            if not users:
                break
            all_users.extend(users)
            index += 1
    return all_users


def ban_user_from_chat(user_id: int, chat_id: int) -> None:
    """Ban user `user_id` in chat `chat_id`"""
    url = get_tg_url(method="banChatMember", user_id=user_id, chat_id=chat_id)
    httpx.get(url).json()


def unban_user_from_chat(user_id: int, chat_id: int) -> None:
    """Unban user `user_id` in chat `chat_id`"""
    url = get_tg_url(method="unbanChatMember", user_id=user_id, chat_id=chat_id)
    httpx.get(url).json()


def main() -> None:
    TG_CHAT_ID = get_telegram_chat_id_by_channel_id(TG_CHANNEL_ID)
    logger.debug(f"Linked chat id is {TG_CHAT_ID}")

    users_in_chat = get_all_chat_users(TG_CHAT_ID)
    users_in_chat_count = len(users_in_chat)
    logger.debug(f"Users in chat: {users_in_chat_count}")

    for index, user in enumerate(users_in_chat):
        if user.bot:
            if  user.is_self: 
                continue
            logger.warning(
                f"Some strange bot here, skip it now: @{user.username}")
            continue
        is_channel_member = is_user_in_channel(user.id, TG_CHANNEL_ID)
        if not is_channel_member:
            logger.info(
                f"We need to ban+unban user #{user.id}, "
                f"username {user.username}")
            # Uncomment it for ban+unban user
            # ban_user_from_chat(user.id, TG_CHAT_ID)
            # unban_user_from_chat(user.id, TG_CHAT_ID)
        time.sleep(0.5)
        if index and index % 10 == 0:
            logger.debug(f"Processed {index} of {users_in_chat_count} users")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logger.info("KeyboardInterrupt or exit(), goodbye!")
    except Exception as e:
        logger.exception("Uncaught exception")
