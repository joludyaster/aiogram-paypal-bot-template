from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from database.commands.receipts import ReceiptSession
from database.commands.users import UserSession


@dataclass
class RequestsDistributor:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.
    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def users(self) -> UserSession:
        return UserSession(self.session)

    @property
    def receipts(self) -> ReceiptSession:
        return ReceiptSession(self.session)
