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

    async def delete_entry_code(self, telegram_id: int, user_code: UserSetCode):
        is_code_correct = await self.uow.user.check_user_code(telegram_id, entry_code=user_code.code)
        if not is_code_correct:
            raise EntryCodeUpdateError("Failed to delete code. Code is not correct.")

        updated = await self.uow.user.update_user_by_id(telegram_id, entry_code=None)
        if not updated:
            raise EntryCodeUpdateError("Failed to delete entry code.")
