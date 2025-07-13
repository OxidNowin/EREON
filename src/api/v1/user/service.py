from api.v1.base.service import BaseService
from api.v1.user.schemas import UserEmail, UserChangeCode, UserResponse


class UserService(BaseService):
    async def verify_email(self, telegram_id: int, user_email: UserEmail):
        ...

    async def change_entry_code(self, telegram_id: int, codes: UserChangeCode):
        if not await self.uow.user.update_entry_code(telegram_id, codes.old_code, codes.new_code):
            raise
