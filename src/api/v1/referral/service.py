from api.v1.base.service import BaseService
from api.v1.referral.schemas import ReferralInfo, ReferralOperationInfo, ReferralOperationsResponse
from infra.postgres.models import ReferralType
from api.v1.referral.exceptions import ReferralNotFoundError, ReferralTypeAlreadySetError, ReferralUpdateError


class ReferralService(BaseService):
    async def set_referral_type(self, telegram_id: int, referral_type: ReferralType) -> None:
        existing_referral = await self.uow.referral.get_by_id(telegram_id)
        if not existing_referral:
            raise ReferralNotFoundError("Реферал не найден")
        
        if existing_referral.type is not None:
            raise ReferralTypeAlreadySetError("Тип реферальной программы уже установлен и не может быть изменен")
        
        updated = await self.uow.referral.update(telegram_id, type=referral_type)
        if not updated:
            raise ReferralUpdateError("Не удалось обновить тип реферальной программы")

    async def get_referral_info(self, telegram_id: int) -> ReferralInfo:
        referral = await self.uow.referral.get_by_id(telegram_id)
        if not referral:
            raise ReferralNotFoundError("Реферал не найден")
        
        referred_users = await self.uow.referral.get_referred_users(telegram_id)
        referred_user_ids = [user.telegram_id for user in referred_users]

        return ReferralInfo(
            telegram_id=referral.telegram_id,
            referred_by=referral.referred_by,
            code=referral.code,
            active=referral.active,
            referral_type=referral.type,
            referral_count=referral.referral_count,
            balance=referral.balance,
            referred_users=referred_user_ids
        )

    async def get_user_referral_operations(
        self, 
        telegram_id: int, 
        limit: int | None = None, 
        offset: int | None = None
    ) -> ReferralOperationsResponse:
        referral = await self.uow.referral.get_by_id(telegram_id)
        if not referral:
            raise ReferralNotFoundError("Реферал не найден")
        
        operations = await self.uow.referral_operation.get_referral_operations(
            telegram_id, limit=limit, offset=offset
        )
        
        total = await self.uow.referral_operation.count_referral_operations(telegram_id)
        
        operation_infos = [
            ReferralOperationInfo(
                referral_operation_id=op.referral_operation_id,
                status=op.status,
                operation_type=op.operation_type,
                amount=float(op.amount),
                created_at=op.created_at.isoformat()
            )
            for op in operations
        ]
        
        return ReferralOperationsResponse(
            operations=operation_infos,
            total=total,
            limit=limit,
            offset=offset
        )
