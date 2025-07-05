from sqlalchemy import select, update, and_

from infra.postgres.models.user import User
from infra.postgres.storage.base_storage import PostgresStorage


class UserStorage(PostgresStorage[User]):
    model_cls = User

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(self.model_cls).where(self.model_cls.email == email)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user_by_id(self, telegram_id: int, **kwargs) -> User | None:
        stmt = (
            update(self.model_cls)
            .where(self.model_cls.telegram_id == telegram_id)
            .values(**kwargs)
            .returning(self.model_cls)
        )
        result = await self._db.execute(stmt)
        data_source = result.scalar_one_or_none()
        return data_source

    async def check_user_code(self, telegram_id: int, entry_code: str) -> bool:
        stmt = (
            select(self.model_cls.telegram_id)
            .where(
                and_(
                    self.model_cls.telegram_id == telegram_id,
                    self.model_cls.entry_code == entry_code
                )
            )
            .limit(1)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none() is not None
