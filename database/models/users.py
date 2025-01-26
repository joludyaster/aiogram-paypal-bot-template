from typing import Optional

from sqlalchemy import String, BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, TableNameMixin


class User(Base, TimestampMixin, TableNameMixin):
    """
    This class represents a User in the application.
    If you want to learn more about SQLAlchemy and Alembic, you can check out the following link to my course:
    https://www.udemy.com/course/sqlalchemy-alembic-bootcamp/?referralCode=E9099C5B5109EB747126

    Attributes:
    -----------
    user_id [Mapped[int]] -> user's telegram ID.
    username [Mapped[Optional[str]]] -> user's telegram username.
    full_name [Mapped[str]] -> user's telegram full name.

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
    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(String(128))
    full_name: Mapped[str] = mapped_column(String(128))

    def __repr__(self):
        return f"<User {self.user_id} {self.username} {self.full_name}>"
