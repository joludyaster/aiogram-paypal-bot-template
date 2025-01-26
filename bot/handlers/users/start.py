from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.data.config import Config
from bot.paypal.paypal import PaypalProcessor
from database.commands.requests import RequestsDistributor

# Initialize a router
start_router = Router()


@start_router.message(Command("test_payment"))
async def start(message: Message, paypal: PaypalProcessor, config: Config, distributor: RequestsDistributor):
    username_or_full_name = message.from_user.username if message.from_user.username else message.from_user.full_name

    await distributor.users.create_user(
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )

    text = f"""👋 Hello, {username_or_full_name}
This is a test payment for a test.

Use button below to process a test payment ⬇️"""

    await paypal.send_payment(
        user_id=message.from_user.id,
        intent="sale",
        return_url=f"{config.webhook.base_webhook_url}/payment/success?user_id={message.from_user.id}",
        cancel_url=f"{config.webhook.base_webhook_url}/payment/fail?user_id={message.from_user.id}",
        items=[
            {
                "name": "Something precious",
                "description": "This precious item is really rear...",
                "sku": "Yes",
                "price": 3.89,
                "currency": "CAD",
                "quantity": 1
            },
            {
                "name": "Vase",
                "description": "The Vase of the president of the USA",
                "sku": "Really good vase",
                "price": 10.56,
                "currency": "CAD",
                "quantity": 1
            }
        ],
        total=14.45,
        currency="CAD",
        description="Simple description of the payment...",
        text=text
    )
