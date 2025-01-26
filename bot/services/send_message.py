from aiogram import Bot, exceptions
from typing import Union
from aiogram.types import InlineKeyboardMarkup

import logging
import asyncio


async def send_message(
    bot: Bot,
    user_id: Union[int, str],
    text: str,
    disable_notification: bool = False,
    reply_markup: InlineKeyboardMarkup | tuple[InlineKeyboardMarkup] = None,
) -> bool:

    """
    Safe messages' sender.

    :param bot: bot instance.
    :param user_id: user id. If str - must contain only digits.
    :param text: text of the message.
    :param disable_notification: disable notification or not.
    :param reply_markup: reply markup.
    :return: success.
    """

    try:
        await bot.send_message(
            user_id,
            text,
            disable_notification=disable_notification,
            reply_markup=reply_markup[0] if isinstance(reply_markup, tuple) else reply_markup,
        )

    except exceptions.TelegramBadRequest as e:
        logging.error(f"[ERROR] Telegram server says - Bad Request: {e}")
    except exceptions.TelegramForbiddenError:
        logging.error(f"[ERROR] Target [ID:{user_id}]: got TelegramForbiddenError")
    except exceptions.TelegramRetryAfter as e:
        logging.error(
            f"[ERROR] Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
        )
        await asyncio.sleep(e.retry_after)
        return await send_message(
            bot, user_id, text, disable_notification, reply_markup
        )  # Recursive call
    except exceptions.TelegramAPIError:
        logging.error(f"[ERROR] Target [ID:{user_id}]: failed")
    else:
        logging.info(f"[SUCCESS] Target [ID:{user_id}]: success")
        return True
    return False
