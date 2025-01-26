from sqlalchemy.dialects.postgresql import insert

from database.commands.base import BaseDistributor
from database.models.receipts import Receipt


class ReceiptSession(BaseDistributor):
    async def create_receipt(
            self,
            user_id: int,
            payer_email: str,
            payer_first_name: str,
            payer_last_name: str,
            product_name: str,
            product_description: str,
            price: float,
            currency: str,
            quantity: int
    ):
        """
        Function to add a receipt from a successful transaction to the database.

        :param user_id: user's telegram ID.
        :param payer_email: email that was used to pay for the transaction.
        :param payer_first_name: first name that was used to pay for the transaction.
        :param payer_last_name: last name that was used to pay for the transaction.
        :param product_name: product's name that's been paid for.
        :param product_description: product's description that's been paid for.
        :param price: product's price that's been paid for.
        :param currency: product's currency that's been paid for.
        :param quantity: product's quantity that's been paid for.
        :return: Receipt object.
        """

        insert_stmt = (
            insert(Receipt)
            .values(
                user_id=user_id,
                payer_email=payer_email,
                payer_first_name=payer_first_name,
                payer_last_name=payer_last_name,
                product_name=product_name,
                product_description=product_description,
                price=price,
                currency=currency,
                quantity=quantity
            )
            .on_conflict_do_update(
                index_elements=[Receipt.id],
                set_=dict(
                    user_id=user_id,
                    payer_email=payer_email,
                    payer_first_name=payer_first_name,
                    payer_last_name=payer_last_name,
                    product_name=product_name,
                    product_description=product_description,
                    price=price,
                    currency=currency,
                    quantity=quantity
                ),
            )
            .returning(Receipt)
        )
        result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()
