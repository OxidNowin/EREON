import aiohttp
from logging import getLogger

from api.v1.base.service import BaseService
from api.v1.referral.schemas import (
    ReferralInfo,
    ReferralOperationInfo,
    ReferralOperationsResponse,
    ReferralStatsInfo,
    ReferralStatsResponse,
    ReferralDepositOperationInfo,
    ReferralDepositOperationsResponse,
)
from api.v1.referral.levels import (
    get_revenue_share_level,
    get_revenue_share_percentage,
    get_next_level_referrals_needed,
)
from infra.postgres.models import ReferralType
from api.v1.referral.exceptions import ReferralNotFoundError, ReferralTypeAlreadySetError, ReferralUpdateError
from core.config import settings

logger = getLogger(__name__)


class ReferralService(BaseService):
    async def _get_telegram_user_info(self, user_id: int) -> tuple[str | None, str | None]:
        """
        Получить username и avatar_url пользователя через Telegram Bot API.
        
        Returns:
            Кортеж (username, avatar_url) или (None, None) в случае ошибки
        """
        if not settings.telegram_bot_token:
            return None, None
        
        base_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}"
        username = None
        avatar_url = None
        
        try:
            async with aiohttp.ClientSession() as session:
                # Получаем информацию о чате (пользователе)
                async with session.get(f"{base_url}/getChat", params={"chat_id": user_id}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("ok"):
                            chat_info = data.get("result", {})
                            username = chat_info.get("username")
                
                # Получаем фото профиля
                async with session.get(f"{base_url}/getUserProfilePhotos", params={"user_id": user_id, "limit": 1}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("ok"):
                            photos_info = data.get("result", {})
                            if photos_info.get("total_count", 0) > 0:
                                photos = photos_info.get("photos", [])
                                if photos:
                                    # Берем самое большое фото
                                    photo_sizes = photos[0]
                                    if photo_sizes:
                                        largest_photo = photo_sizes[-1]
                                        file_id = largest_photo.get("file_id")
                                        
                                        if file_id:
                                            # Получаем путь к файлу
                                            async with session.get(f"{base_url}/getFile", params={"file_id": file_id}) as file_resp:
                                                if file_resp.status == 200:
                                                    file_data = await file_resp.json()
                                                    if file_data.get("ok"):
                                                        file_path = file_data.get("result", {}).get("file_path")
                                                        if file_path:
                                                            avatar_url = f"https://api.telegram.org/file/bot{settings.telegram_bot_token}/{file_path}"
        except Exception as e:
            logger.error(f"Error getting Telegram user info for {user_id}: {e}", exc_info=True)
        
        return username, avatar_url

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

        referral_spending = 0
        if referral.type == ReferralType.FIXED_INCOME:
            referral_spending = await self.uow.operation.get_total_referrals_spending(referred_user_ids)

        referral_count = referral.referral_count or 0
        level = get_revenue_share_level(referral_count)
        level_percentage = float(get_revenue_share_percentage(referral_count) * 100)
        next_level_needed = get_next_level_referrals_needed(referral_count)

        return ReferralInfo(
            telegram_id=referral.telegram_id,
            referred_by=referral.referred_by,
            code=referral.code,
            active=referral.active,
            referral_type=referral.type,
            referral_spending=referral_spending,
            referral_count=referral.referral_count,
            balance=referral.balance,
            referred_users=referred_user_ids,
            level=level,
            level_percentage=level_percentage,
            next_level_referrals_needed=next_level_needed,
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

    async def get_referrals_stats(
        self,
        telegram_id: int,
        limit: int | None = None,
        offset: int | None = None
    ) -> ReferralStatsResponse:
        """Получает статистику по приглашенным рефералам с пагинацией"""
        referral = await self.uow.referral.get_by_id(telegram_id)
        if not referral:
            raise ReferralNotFoundError("Реферал не найден")
        
        # Получаем список приглашенных рефералов с пагинацией
        referred_users = await self.uow.referral.get_referred_users(telegram_id)
        total_referrals = len(referred_users)
        
        # Применяем пагинацию
        if offset is not None and limit is not None:
            referred_users = referred_users[offset:offset + limit]
        elif offset is not None:
            referred_users = referred_users[offset:]
        elif limit is not None:
            referred_users = referred_users[:limit]
        
        # Получаем общую сумму, полученную от всех рефералов
        total_earned = await self.uow.referral_operation.get_referrer_total_earned(telegram_id)
        total_earned_float = float(total_earned)
        
        # Формируем статистику для каждого реферала
        referrals_stats = []
        for referred_user in referred_users:
            # Получаем сумму, полученную от этого реферала
            earned_amount = await self.uow.referral_operation.get_referral_total_earned(
                telegram_id, 
                referred_user.telegram_id
            )
            earned_amount_float = float(earned_amount)
            
            percentage: float | None = None
            if referral.type == ReferralType.FIXED_INCOME:
                CPA_THRESHOLD = 150.0
                user_spending = await self.uow.operation.get_user_total_spending(referred_user.telegram_id)
                user_spending_float = float(user_spending)

                if user_spending_float >= CPA_THRESHOLD:
                    percentage = 100.0
                else:
                    percentage = (user_spending_float / CPA_THRESHOLD) * 100

            level = get_revenue_share_level(referred_user.referral_count or 0)

            # Получаем username и avatar_url через Telegram Bot API
            username, avatar_url = await self._get_telegram_user_info(referred_user.telegram_id)

            referrals_stats.append(
                ReferralStatsInfo(
                    telegram_id=referred_user.telegram_id,
                    username=username,
                    avatar_url=avatar_url,
                    earned_amount=earned_amount_float,
                    percentage=round(percentage, 2) if percentage is not None else None,
                    level=level,
                )
            )
        
        return ReferralStatsResponse(
            referrals=referrals_stats,
            referral_type=referral.type,
            total=total_referrals,
            total_earned=total_earned_float,
            limit=limit,
            offset=offset
        )

    async def get_deposit_operations(
        self,
        telegram_id: int,
        limit: int | None = None,
        offset: int | None = None
    ) -> ReferralDepositOperationsResponse:
        """Получает последние операции начисления на реферальный счет с информацией о рефералах"""
        referral = await self.uow.referral.get_by_id(telegram_id)
        if not referral:
            raise ReferralNotFoundError("Реферал не найден")
        
        # Получаем операции начисления (DEPOSIT)
        operations = await self.uow.referral_operation.get_deposit_operations_with_source(
            telegram_id, limit=limit, offset=offset
        )
        
        # Подсчитываем общее количество операций начисления
        total = await self.uow.referral_operation.count_deposit_operations(telegram_id)
        
        # Получаем суммарное количество приглашенных пользователей
        referred_users = await self.uow.referral.get_referred_users(telegram_id)
        total_referrals = len(referred_users)
        
        # Формируем информацию об операциях с данными о рефералах
        operation_infos = []
        for op in operations:
            source_username = None
            source_avatar_url = None
            
            # Получаем информацию о реферале, который начислил (если есть source_referral_id)
            if op.source_referral_id:
                source_username, source_avatar_url = await self._get_telegram_user_info(op.source_referral_id)
            
            operation_infos.append(
                ReferralDepositOperationInfo(
                    referral_operation_id=op.referral_operation_id,
                    status=op.status,
                    amount=float(op.amount),
                    created_at=op.created_at.isoformat(),
                    source_referral_id=op.source_referral_id,
                    source_username=source_username,
                    source_avatar_url=source_avatar_url
                )
            )
        
        return ReferralDepositOperationsResponse(
            operations=operation_infos,
            total=total,
            total_referrals=total_referrals,
            limit=limit,
            offset=offset
        )
