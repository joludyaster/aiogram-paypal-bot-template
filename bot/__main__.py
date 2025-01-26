import logging

import betterlogging
from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from bot.middlewares.middlewares import LoggingMiddleware, ConfigMiddleware, DatabaseMiddleware, PaypalMiddleware
from bot.paypal.paypal import PaypalProcessor
from bot.services.broadcast import broadcast
from data.config import load_config
from database.setup import create_engine, run_migrations, create_session_pool
from handlers import routers_list

config = load_config("../.env.dist")


def setup_logging() -> None:
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    It sets the log level to INFO and configures a basic colorized log for
    output. The log format includes the filename, line number, log level,
    timestamp, logger name, and log message.
    """

    log_level = logging.INFO
    betterlogging.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("[INFO] Starting bot")


def register_global_middlewares(dp: Dispatcher, paypal: PaypalProcessor) -> None:
    """
    Register global middlewares for the given dispatcher.
    Global middlewares here are the ones that are applied to all the handlers (you specify the type of update)

    :param paypal: PayPal instance.
    :param dp: the dispatcher instance.
    :type dp: dispatcher.
    """

    middleware_types = [
        ConfigMiddleware(config),
        LoggingMiddleware(),
        PaypalMiddleware(paypal=paypal)
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


async def on_startup(bot: Bot) -> None:
    try:
        await bot.set_webhook(f"{config.webhook.base_webhook_url}/webhook", secret_token=config.webhook.web_secret,
                              allowed_updates=[])
    except TelegramNetworkError as e:
        logging.error(f"Failed to set webhook: {e}")

    await broadcast(
        bot=bot,
        users=config.telegram_bot.admin_ids,
        text="👋 Hello, admin! Your bot has been started successfully."
    )

    await bot.set_my_commands(
        [
            BotCommand(
                command="/test_payment",
                description="Perform test payment."
            )
        ]
    )

    # Set up the database
    engine = create_engine(config.database, echo=True)
    await run_migrations(engine)


async def on_shutdown(bot: Bot) -> None:
    try:
        logging.info("Deleting webhook and dropping all pending updates...")
        async with bot.session:
            await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Webhook has been deleted and all pending updates have been dropped.")
    except TelegramNetworkError as e:
        logging.error(f"Failed to delete webhook: {e}")


def main() -> None:
    # Register logging settings
    setup_logging()

    # Initialize a local storage for aiogram
    storage = MemoryStorage()

    # Initialize PaypalProcessor
    paypal = PaypalProcessor(config=config)

    # Initialize bot instance
    bot = Bot(token=config.telegram_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Initialize a dispatcher
    dp = Dispatcher(storage=storage)

    # Register on startup and on shutdown functions
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Include routers in the dispatcher
    dp.include_routers(*routers_list)

    # Initialize a web application
    app = web.Application()
    app.router.add_get("/payment/success", paypal.check_payment)

    # Register global middlewares
    register_global_middlewares(dp=dp, paypal=paypal)

    # Initialize database dependencies such as engine and session pool and register a pool in the middleware
    engine = create_engine(config.database)
    session_pool = create_session_pool(engine)
    dp.update.outer_middleware(DatabaseMiddleware(session_pool))

    # Initialize a simple request handler for the webhook
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=config.webhook.web_secret
    )

    # Register webhook command for the webhook
    webhook_requests_handler.register(app, path=f"/webhook")

    # Set up an application
    setup_application(app, dp, bot=bot)

    # Run a web app
    web.run_app(app, host=config.webhook.web_server_host, port=config.webhook.web_server_port)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot was shut off!")
