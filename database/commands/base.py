from sqlalchemy.ext.asyncio import AsyncSession


class BaseDistributor:
    """
    A class representing a base repository for handling database operations.

    Attributes:
    -----------
    session [AsyncSession] -> the database session used by the distributor.
    """

    def __init__(self, session):
        self.session: AsyncSession = session
