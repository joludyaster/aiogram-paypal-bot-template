from dataclasses import dataclass
from typing import Optional

from environs import Env
from sqlalchemy.engine.url import URL


@dataclass
class DatabaseConfig:
    """
    Database configuration class.
    This class holds various settings for the database configuration like such database host, password, port, etc.

    Attributes
    ----------
    host [str] -> host of the database.
    password [str] -> password of the database.
    user [str] -> username of the database.
    database [str] -> name of the database.
    port [str] -> port of the database.
    """

    host: str
    password: str
    user: str
    database: str
    port: int = 5432

    def construct_sqlalchemy_url(self, driver="asyncpg", host=None, port=None) -> str:
        """
        Function to construct SQLAlchemy URL for database connection.

        :param driver: driver that's used to help with database connection.
        :param host: host of the database.
        :param port: port of the database
        :return: SQLAlchemy URL as a string.
        """

        if not host:
            host = self.host
        if not port:
            port = self.port
        uri = URL.create(
            drivername=f"postgresql+{driver}",
            username=self.user,
            password=self.password,
            host=host,
            port=port,
            database=self.database,
        )
        return uri.render_as_string(hide_password=False)

    @staticmethod
    def from_env(env: Env):
        """
        This function takes arguments from environmental variables and creates a DatabaseConfig configuration config.

        :param env: environmental tool to take arguments.
        :return: DatabaseConfig configuration config.
        """
        host = env.str("DB_HOST")
        password = env.str("POSTGRES_PASSWORD")
        user = env.str("POSTGRES_USER")
        database = env.str("POSTGRES_DB")
        port = env.int("DB_PORT", 5432)
        return DatabaseConfig(
            host=host, password=password, user=user, database=database, port=port
        )


@dataclass
class TelegramBotConfig:
    """
    Creates the TelegramBotConfig object from environment variables.
    """

    token: str
    admin_ids: list[int]
    use_redis: bool

    @staticmethod
    def from_env(env: Env):
        """
        This function takes arguments from environmental variables and creates a TelegramBotConfig configuration config.

        :param env: environmental tool to take arguments.
        :return: TelegramBotConfig configuration config.
        """
        token = env.str("BOT_TOKEN")
        admin_ids = list(map(int, env.list("ADMINS")))
        use_redis = env.bool("USE_REDIS")
        return TelegramBotConfig(token=token, admin_ids=admin_ids, use_redis=use_redis)


@dataclass
class WebhookConfig:
    """
    Webhook configuration class.
    This class holds various settings for the webhook configuration like webhook host, port, secret key and url

    Attributes
    ----------
    web_server_host [str] -> host where the webhook is located.
    web_server_port [int] -> port of the webhook.
    web_secret [str] -> secret key of the webhook for authorization and to prevent hacker attacks.
    base_webhook_url [str] -> url of the webhook, e.g. https://your_webhook_url
    """

    web_server_host: str
    web_server_port: int
    web_secret: str
    base_webhook_url: str

    @staticmethod
    def from_env(env: Env):
        """
        This function takes arguments from environmental variables and creates a WebhookConfig configuration config.

        :param env: environmental tool to take arguments.
        :return: WebhookConfig configuration config.
        """

        web_server_host = env.str("WEB_SERVER_HOST")
        web_server_port = env.int("WEB_SERVER_PORT")
        web_secret = env.str("WEB_SECRET")
        base_webhook_url = env.str("BASE_WEBHOOK_URL")

        return WebhookConfig(
            web_server_host=web_server_host,
            web_server_port=web_server_port,
            web_secret=web_secret,
            base_webhook_url=base_webhook_url
        )


@dataclass
class PaypalConfig:
    """
    PayPal configuration class.
    This class holds various settings for the PayPal configuration like webhook host, port, secret key and url

    Attributes
    ----------
    paypal_mode [str] -> mode of the PayPal payments ("sandbox" or "live").
    paypal_client_id [str] -> id of the user for authentication.
    paypal_client_secret [str] -> secret key of the user for authentication.
    """

    paypal_mode: str
    paypal_client_id: str
    paypal_client_secret: str

    @staticmethod
    def from_env(env: Env):
        """
        This function takes arguments from environmental variables and creates a PaypalConfig configuration config.

        :param env: environmental tool to take arguments.
        :return: PaypalConfig configuration config.
        """

        paypal_mode = env.str("PAYPAL_MODE")
        paypal_client_id = env.str("PAYPAL_CLIENT_ID")
        paypal_client_secret = env.str("PAYPAL_CLIENT_SECRET")

        return PaypalConfig(paypal_mode=paypal_mode, paypal_client_id=paypal_client_id,
                            paypal_client_secret=paypal_client_secret)


@dataclass
class Config:
    """
    The main configuration class that integrates all the other configuration classes.
    This class holds the other configuration classes, providing a centralized point of access for all settings.

    Attributes
    ----------
    telegram_bot [TelegramBotConfig] -> holds various settings related to the Telegram Bot.
    paypal [PaypalConfig] -> holds various settings related to the PayPal configuration.
    webhook [WebhookConfig] -> holds various settings related to the Webhook configuration.
    database [Optional[DatabaseConfig]] -> holds various settings related to the database configuration.
    """

    telegram_bot: TelegramBotConfig
    paypal: PaypalConfig
    webhook: WebhookConfig
    database: Optional[DatabaseConfig] = None


def load_config(path: str = None) -> Config:
    """
    This function takes an optional file path as input and returns a Config object.

    :param path: the path of .env.dist file from where to load the configuration variables.
    :return: config object with attributes set as per environment variables.
    """

    env = Env()
    env.read_env(path)

    return Config(
        telegram_bot=TelegramBotConfig.from_env(env),
        paypal=PaypalConfig.from_env(env),
        database=DatabaseConfig.from_env(env),
        webhook=WebhookConfig.from_env(env)
    )
