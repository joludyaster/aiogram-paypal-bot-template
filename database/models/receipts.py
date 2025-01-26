from sqlalchemy import String, Integer, BIGINT, FLOAT
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, TableNameMixin, int_pk


class Receipt(Base, TimestampMixin, TableNameMixin):
    """
    This class represents a Receipt in the application.
    If you want to learn more about SQLAlchemy and Alembic, you can check out the following link to my course:
    https://www.udemy.com/course/sqlalchemy-alembic-bootcamp/?referralCode=E9099C5B5109EB747126

    Attributes:
    -----------
    id [Mapped[int_pk]] -> id of the object in the database.
    user_id [Mapped[int]] -> user's telegram ID.
    payer_email [Mapped[str]] -> email that was used to pay for the transaction.
    payer_first_name [Mapped[str]] -> first name that was used to pay for the transaction.
    payer_last_name [Mapped[str]] -> last name that was used to pay for the transaction.
    product_name [Mapped[str]] -> product's name that's been paid for.
    product_description [Mapped[str]] -> product's description that's been paid for.
    price [Mapped[float]] -> product's price that's been paid for.
    currency [Mapped[str]] -> product's currency that's been paid for.
    quantity [Mapped[int]] -> product's quantity that's been paid for.

    Methods:
    --------
    __repr__() -> returns a string representation of the User object.

    Inherited Attributes:
    ---------------------
    Inherits from Base, TimestampMixin, and TableNameMixin classes, which provide additional attributes and functionality.

    Inherited Methods:
    ------------------
    Inherits methods from Base, TimestampMixin, and TableNameMixin classes, which provide additional functionality.
    """

    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(BIGINT)
    payer_email: Mapped[str] = mapped_column(String(128))
    payer_first_name: Mapped[str] = mapped_column(String(128))
    payer_last_name: Mapped[str] = mapped_column(String(128))
    product_name: Mapped[str] = mapped_column(String(128))
    product_description: Mapped[str] = mapped_column(String(256))
    price: Mapped[float] = mapped_column(FLOAT)
    currency: Mapped[str] = mapped_column(String(3))
    quantity: Mapped[int] = mapped_column(Integer)

    def __repr__(self):
        return (f"<Receipt {self.user_id} {self.payer_email} {self.payer_first_name} "
                f"{self.payer_last_name} {self.product_name} {self.product_description} "
                f"{self.price} {self.currency} {self.quantity}")
