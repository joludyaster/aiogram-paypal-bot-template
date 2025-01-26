from typing import Optional

from sqlalchemy.dialects.postgresql import insert

from database.commands.base import BaseDistributor
from database.models.users import User


class UserSession(BaseDistributor):
    async def create_user(
            self,
            user_id: int,
            full_name: str,
            username: Optional[str] = None,
    ):
        """
        Creates a new user in the database and returns the user object.

        :param user_id: user's telegram ID.
        :param full_name: user's telegram full name.
        :param username: user's telegram username. It's an optional parameter.
        :return: User object.
        """

        insert_stmt = (
            insert(User)
            .values(
                user_id=user_id,
                username=username,
                full_name=full_name
            )
            .on_conflict_do_update(
                index_elements=[User.user_id],
                set_=dict(
                    username=username,
                    full_name=full_name
                ),
            )
            .returning(User)
        )
        result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()
