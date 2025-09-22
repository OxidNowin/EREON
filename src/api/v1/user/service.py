from api.v1.base.service import BaseService
from api.v1.user.schemas import UserEmail, UserChangeCode, UserSetCode
from api.v1.user.exceptions import EntryCodeUpdateError


class UserService(BaseService):
    async def verify_email(self, telegram_id: int, user_email: UserEmail):
        ...

    async def change_entry_code(self, telegram_id: int, codes: UserChangeCode):
        updated = await self.uow.user.update_entry_code(telegram_id, codes.old_code, codes.new_code)
        if not updated:
            raise EntryCodeUpdateError("Failed to update entry code. Old code may be incorrect.")

    async def set_entry_code(self, telegram_id: int, user_code: UserSetCode):
        has_entry_code = await self.uow.user.has_entry_code(telegram_id)
        if has_entry_code:
            raise EntryCodeUpdateError("Failed to set entry code. Code already exists.")

        updated = await self.uow.user.update_user_by_id(telegram_id, entry_code=user_code.code)
        if not updated:
            raise EntryCodeUpdateError("Failed to update entry code.")
