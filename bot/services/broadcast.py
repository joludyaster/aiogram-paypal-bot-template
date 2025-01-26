from typing import Union
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from bot.services.send_message import send_message

import asyncio
import logging


async def broadcast(
    bot: Bot,
    users: list[Union[str, int]],
    text: str,
    disable_notification: bool = False,
    reply_markup: InlineKeyboardMarkup = None,
) -> int:

    """
    Simple broadcaster.

    :param bot: bot instance.
    :param users: list of users.
    :param text: text of the message.
    :param disable_notification: disable notification or not.
    :param reply_markup: reply markup.
    :return: count of messages.
    """

    count = 0
    try:
        for user_id in users:
            async with bot.session:
                if await send_message(
                    bot, user_id, text, disable_notification, reply_markup
                ):
                    count += 1
                await asyncio.sleep(
                    0.05
                )  # 20 messages per second (Limit: 30 messages per second)
    finally:
        logging.info(f"[SUCCESS] {count} messages successful sent.")

    return count
