import logging
from typing import List, Dict

import paypalrestsdk
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web
from paypalrestsdk.exceptions import InvalidConfig
from sqlalchemy.ext.asyncio import AsyncSession

from bot.data.config import Config
from bot.services.send_message import send_message
from database.commands.requests import RequestsDistributor
from database.setup import create_engine


class PaypalProcessor:
    def __init__(self, config: Config):
        self.config = config
        self.paypal = paypalrestsdk

    def configuration(self) -> bool:
        """
        Function to configure PayPal.

        :return: True if configuration was successful, False otherwise
        """

        paypal_config = {
            "mode": self.config.paypal.paypal_mode,
            "client_id": self.config.paypal.paypal_client_id,
            "client_secret": self.config.paypal.paypal_client_secret
        }

        try:
            self.paypal.configure(paypal_config)
            return True
        except InvalidConfig as error:
            logging.error(f"Couldn't configure paypal: {error}")
            return False

    async def send_payment(
            self,
            user_id: int | str,
            intent: str,
            return_url: str,
            cancel_url: str,
            items: List[Dict],
            total: float,
            currency: str,
            description: str,
            text: str
    ):
        """
        Class method to create a payment link.

        :param user_id: id of a user (you can parse the link later to send a confirmation to the user).
        :param intent: type of payment ("sale", "order", "authorize")
        :param return_url: the URL where the payer is redirected after he or she approves the payment.
        :param cancel_url: the URL where the payer is redirected after he or she cancels the payment.
        :param items: list of keyword items

            Usage::

                -> items=[
                    {
                        "name": "Something precious",
                        "description": "This precious item is really rare..."
                        "sku": "Yes",
                        "price": 1,
                        "currency": "CAD",
                        "quantity": 1
                    }
                ],

        :param total: total of the payment.
        :param currency: currency of the payment.
        :param description: description of the payment.
        :param text: message text.
        :return:
        """
        bot = Bot(
            token=self.config.telegram_bot.token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

        payment = paypalrestsdk.Payment(
            {
                "intent": intent,
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": cancel_url
                },
                "transactions": [{
                    "item_list": {
                        "items": items
                    },
                    "amount": {
                        "total": total,
                        "currency": currency},
                    "description": description}]
            }
        )

        if payment.create():
            approval_url = ""
            for link in payment.links:
                if link.rel == 'approval_url':
                    approval_url = link.href
                    break

            async with bot.session:
                return await send_message(
                    bot=bot,
                    user_id=user_id,
                    text=text,
                    disable_notification=False,
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text=f"Pay ${total} {currency}", web_app=WebAppInfo(url=f"{approval_url}")
                                )
                            ]
                        ]
                    ),
                )

    async def check_payment(self, request: web.Request):
        """
        Function to check a status of the payment.
        If successful, sends a successful web response and sends a message to the user about the transaction details.

        :param request: web.Request type of object.
        :return: web.Request message.
        """

        bot = Bot(
            token=self.config.telegram_bot.token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

        payment_id = request.query.get('paymentId')
        payer_id = request.query.get('PayerID')
        user_id = request.query.get("user_id")

        if not payment_id or not payer_id:
            return web.Response(text="Missing paymentId or PayerID.", status=400)

        try:
            # Find the payment by its ID
            payment = paypalrestsdk.Payment.find(payment_id)

            if not payment.execute({"payer_id": payer_id}):
                logging.error(f"[ERROR] Payment execution failed: {payment.error}")
                return web.Response(text="Payment failed or cancelled.", status=400)

            try:
                payer = payment["payer"]
                transactions = payment["transactions"][0]
                if not payer or not transactions:
                    logging.error("[EXCEPTION] Missing payer information or transactions.")
                    return web.Response(text="Missing payer information or transactions.", status=400)

            except KeyError as error:
                logging.error(f"An error occurred while processing the payment.\n{error}")
                return web.Response(text="An error occurred while processing the payment.", status=500)

            payer_email = payer["payer_info"]["email"]
            payer_first_name = payer["payer_info"]["first_name"]
            payer_last_name = payer["payer_info"]["last_name"]

            payment_details = f"""🎉 Congratulations! Payment has been received successfully!

Here's your payment details:

<i>Personal information:</i>
📩 <b>Email:</b> {payer_email}
1️⃣ <b>First name:</b> {payer_first_name}
2️⃣ <b>Last Name:</b> {payer_last_name}

<i>PRODUCTS</i>"""

            transaction_payment_description = transactions["description"]

            for item in transactions["item_list"]["items"]:
                transformed_item = item.to_dict()

                item = transformed_item["name"]
                item_description = transformed_item["description"]
                item_price = transformed_item["price"]
                item_currency = transformed_item["currency"]
                item_quantity = transformed_item["quantity"]

                engine = create_engine(self.config.database, echo=True)
                async with AsyncSession(bind=engine) as session:
                    requests_distributor = RequestsDistributor(session)

                    receipt_result = await requests_distributor.receipts.create_receipt(
                        user_id=int(user_id),
                        payer_email=payer_email,
                        payer_first_name=payer_first_name,
                        payer_last_name=payer_last_name,
                        product_name=item,
                        product_description=transaction_payment_description,
                        price=float(item_price),
                        currency=item_currency,
                        quantity=int(item_quantity)
                    )

                    if receipt_result:
                        logging.info(f"[INFO] Successfully added a receipt to the user with id -> [ID: {user_id}].")
                    else:
                        logging.info(f"[ERROR] Couldn't add a receipt to the user with id -> [ID: {user_id}].")

                payment_details += f"""
                
<i>Product information:</i>
🔍 <b>Product:</b> {item}
💰 <b>Price:</b> ${item_price}
💲 <b>Currency:</b> {item_currency}
🔢 <b>Quantity:</b> {item_quantity}
✏️ <b>Description:</b> {item_description}"""

            payment_details += f"""
            
<b>TOTAL:</b> ${transactions["amount"]["total"]} {transactions["amount"]["currency"]}"""

            logging.info("[SUCCESS] Payment executed successfully.")

            async with bot.session:
                await send_message(
                    bot=bot, user_id=user_id, text=payment_details
                )

            return web.Response(text="Payment successful!")
        except paypalrestsdk.ResourceNotFound as e:
            logging.error(f"[ERROR] Payment not found: \n{e}")
            return web.Response(text="Payment not found.", status=404)
        except Exception as e:
            logging.error(f"[ERROR] Error executing payment: \n{e}")
            return web.Response(text="An error occurred while processing the payment.", status=500)
