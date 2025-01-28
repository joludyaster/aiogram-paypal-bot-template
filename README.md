<div align="center" dir="auto">
<pre>
 █████╗ ██╗ ██████╗ ██████╗ ██████╗ ████████╗
██╔══██╗██║██╔═══██╗██╔══██╗██╔══██╗╚══██╔══╝
███████║██║██║   ██║██████╔╝██████╔╝   ██║   
██╔══██║██║██║   ██║██╔═══╝ ██╔══██╗   ██║   
██║  ██║██║╚██████╔╝██║     ██████╔╝   ██║   
╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═════╝    ╚═╝   
-----------------------------------------------
Telegram bot template + PayPal integration using aiogram, web app and paypalrestsdk    
</pre>
</div>

[AIOPBT](https://github.com/joludyaster/aiogram-paypal-bot-template) -  is a Python-based Telegram bot template built with the [aiogram](https://docs.aiogram.dev/en/dev-3.x/) library, featuring a web app webhook powered by [aiohttp](https://docs.aiohttp.org/en/stable/) and integrated with [Paypalrestsdk](https://github.com/avidas/rest-api-sdk-python) for payment processing. The bot leverages a [PostgreSQL](https://www.postgresql.org/) database, utilizing [SQLAlchemy](https://www.sqlalchemy.org/) as its engine for efficient query handling.

### Technologies used
1. [Aiogram](https://docs.aiogram.dev/en/dev-3.x/)
2. [Aiohttp](https://docs.aiohttp.org/en/stable/)
3. [Paypalrestsdk](https://github.com/avidas/rest-api-sdk-python)
4. [PostgreSQL](https://www.postgresql.org/)
5. [SQLAlchemy](https://www.sqlalchemy.org/)

### Bot structure

```
...
├── bot
    ├── data
        ├── __init__.py
        ├── config.py
    ├── handlers
        ├── users
            ├── __init__.py
            ├── start.py
        ├── __init__.py
    ├── keyboard
        ├── default_keyboard
            ├── __init__.py
            ├── default_keyboard.py
        ├── inline_keyboard
            ├── __init__.py
            ├── inline_keyboard.py
        ├── __init__.py
    ├── middlewares
        ├── __init__.py
        ├── middlewares.py
    ├── paypal
        ├── __init__.py
        ├── paypal.py
    ├── services
        ├── __init__.py
        ├── broadcast.py
        ├── send_message.py
    ├── __init__.py
    ├── __main__.py

├── database
    ├── commands
        ├── __init__.py
        ├── base.py
        ├── receipts.py
        ├── requests.py
        ├── users.py
    ├── models
        ├── __init__.py
        ├── base.py
        ├── receipts.py
        ├── users.py
    ├── __init__.py
    ├── setup.py
├── .env.dist
```

## How to run?

Application requires [Python](https://www.python.org/downloads/) 3.10+ < installed on your local machine to support all features.

> Create virtual environment to install all needed dependencies:

Manually:

```python
python -m venv .venv
```

Or you can use your IDE to install it automatically as for example PyCharm does.

> Install all needed dependencies:

```python
pip install -r requirements.txt
```

> Change .env settings:

```python
DB_HOST=your_database_host
POSTGRES_PASSWORD=your_database_password
POSTGRES_USER=your_database_username
POSTGRES_DB=your_database_table
DB_PORT=5432
ADMINS=list_of_admin_ids

BOT_TOKEN=bot_token
USE_REDIS=False

# Paypal credentials
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret

# Web server settings
WEB_SERVER_HOST=your_webhook_host
WEB_SERVER_PORT=your_webhook_port
WEB_SECRET=your_webhook_secret
BASE_WEBHOOK_URL=your_webhook_url
```

### How to get PayPal credentials?

1. Open [Paypal Developer page](developer.paypal.com) and register with your usual PayPal credentials.
2. Go to [Dashboard](https://developer.paypal.com/dashboard)
3. Scroll down and press [Sandbox accounts](https://developer.paypal.com/dashboard/accounts)
4. Create a new personal and business (by default you will have them both already created)
5. Navigate to [Apps & Credentials](https://developer.paypal.com/dashboard/applications/sandbox)
6. Click on your default app and copy Client ID and Secret key

### How to get webhook details?

If you don't have your own webhook server, you can use [Ngrok](https://ngrok.com/).

1. Install [Ngrok](https://ngrok.com/) on your local machine.
2. Type `ngrok http 8080`

> Port can be different, depending on your allowed ports by your network.

3. Copy the address and paste it in the `.env.dist` file with the rest of the details.

```python
WEB_SERVER_HOST=127.0.0.1
WEB_SERVER_PORT=8080
WEB_SECRET=secret
BASE_WEBHOOK_URL=https://....ngrok-free.app
```

Lastly, just run `__main.py__` file.
