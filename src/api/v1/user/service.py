from api.v1.base.service import BaseService
from api.v1.user.schemas import UserEmail, UserChangeCode
from api.v1.user.exceptions import EntryCodeUpdateError


class UserService(BaseService):
    async def verify_email(self, telegram_id: int, user_email: UserEmail):
        ...

    async def change_entry_code(self, telegram_id: int, codes: UserChangeCode):
        updated = await self.uow.user.update_entry_code(telegram_id, codes.old_code, codes.new_code)
        if not updated:
            raise EntryCodeUpdateError("Failed to update entry code. Old code may be incorrect.")
