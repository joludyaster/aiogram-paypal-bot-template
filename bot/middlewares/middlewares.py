import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from bot.paypal.paypal import PaypalProcessor
from database.commands.requests import RequestsDistributor


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        logging.info(f"[UPDATE] Incoming update: {event}")
        return await handler(event, data)


class ConfigMiddleware(BaseMiddleware):
    def __init__(self, config) -> None:
        self.config = config

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        data["config"] = self.config
        return await handler(event, data)


class PaypalMiddleware(BaseMiddleware):
    def __init__(self, paypal: PaypalProcessor) -> None:
        self.paypal = paypal

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        self.paypal.configuration()
        data["paypal"] = self.paypal
        return await handler(event, data)


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_pool) -> None:
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            distributor = RequestsDistributor(session)
            data["session"] = session
            data["distributor"] = distributor

            result = await handler(event, data)
        return result
