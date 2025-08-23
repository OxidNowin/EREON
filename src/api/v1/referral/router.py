from fastapi import APIRouter, status

from api.v1.referral.schemas import (
    ReferralTypeSet, 
    ReferralInfo, 
    ReferralOperationsResponse
)
from api.v1.referral.dependencies import ReferralServiceDep
from api.v1.auth.dependencies import UserAuthDep
from api.v1.base.dependencies import PaginationDep

router = APIRouter(prefix="/referral", tags=["Referral"])


@router.patch(
    "/type", 
    status_code=status.HTTP_202_ACCEPTED,
    summary="Установить тип реферальной программы",
    description="Устанавливает тип реферальной программы для пользователя.\n\n"
               "**Важно:** Тип можно установить только один раз и изменить его впоследствии нельзя.\n\n"
               "**Доступные типы:**\n"
               "- `FIXED_INCOME` - фиксированный доход за каждого приглашенного пользователя\n"
               "- `PERCENTAGE_INCOME` - процентный доход от операций приглашенных пользователей\n\n"
               "**Требования:**\n"
               "- Пользователь должен быть авторизован\n"
               "- У пользователя должен быть создан реферальный аккаунт\n"
               "- Тип реферальной программы еще не должен быть установлен",
    responses={
        202: {
            "description": "Тип реферальной программы успешно установлен",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Тип реферальной программы установлен"
                    }
                }
            }
        },
        400: {
            "description": "Ошибка обновления реферальной программы",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Не удалось обновить тип реферальной программы",
                        "type": "ReferralUpdateError"
                    }
                }
            }
        },
        404: {
            "description": "Реферал не найден",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Реферал не найден",
                        "type": "ReferralNotFoundError"
                    }
                }
            }
        },
        409: {
            "description": "Тип реферальной программы уже установлен",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Тип реферальной программы уже установлен и не может быть изменен",
                        "type": "ReferralTypeAlreadySetError"
                    }
                }
            }
        }
    }
)
async def set_referral_type(
    user: UserAuthDep,
    referral_type_data: ReferralTypeSet,
    service: ReferralServiceDep
):
    """
    Установить тип реферальной программы.
    
    Позволяет пользователю выбрать один из двух типов реферальной программы:
    - Фиксированный доход за каждого приглашенного пользователя
    - Процентный доход от операций приглашенных пользователей
    
    Тип устанавливается один раз и не может быть изменен впоследствии.
    """
    await service.set_referral_type(user.id, referral_type_data.referral_type)


@router.get(
    "", 
    status_code=status.HTTP_200_OK, 
    response_model=ReferralInfo,
    summary="Получить информацию о реферале",
    description="Возвращает полную информацию о реферальном аккаунте пользователя.\n\n"
               "**Возвращаемая информация:**\n"
               "- Основные данные реферала (ID, код приглашения, активность)\n"
               "- Тип реферальной программы (если установлен)\n"
               "- Количество приглашенных пользователей\n"
               "- Текущий баланс реферальных начислений\n"
               "- Список ID приглашенных пользователей\n"
               "- Информация о том, кто пригласил данного пользователя\n\n"
               "**Требования:**\n"
               "- Пользователь должен быть авторизован\n",
    responses={
        200: {
            "description": "Информация о реферале успешно получена",
            "content": {
                "application/json": {
                    "example": {
                        "telegram_id": 123456789,
                        "referred_by": 987654321,
                        "code": "abc123def456",
                        "active": True,
                        "referral_type": "FIXED_INCOME",
                        "referral_count": 5,
                        "balance": 1000,
                        "referred_users": [111111111, 222222222, 333333333, 444444444, 555555555]
                    }
                }
            }
        },
        404: {
            "description": "Реферал не найден",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Реферал не найден",
                        "type": "ReferralNotFoundError"
                    }
                }
            }
        }
    }
)
async def get_referral_info(
    user: UserAuthDep,
    service: ReferralServiceDep
):
    """
    Получить полную информацию о реферале.
    
    Возвращает детальную информацию о реферальном аккаунте пользователя,
    включая статистику, баланс и список приглашенных пользователей.
    """
    return await service.get_referral_info(user.id)


@router.get(
    "/operations", 
    status_code=status.HTTP_200_OK, 
    response_model=ReferralOperationsResponse,
    summary="Получить операции реферала",
    description="Возвращает список операций реферального аккаунта с поддержкой пагинации.\n\n"
               "**Возвращаемая информация:**\n"
               "- Список операций с детальной информацией\n"
               "- Общее количество операций\n"
               "- Параметры пагинации (лимит и смещение)\n\n"
               "**Типы операций:**\n"
               "- `deposit` - пополнение реферального баланса\n"
               "- `withdraw` - вывод средств с реферального баланса\n\n"
               "**Статусы операций:**\n"
               "- `confirmed` - операция подтверждена\n"
               "- `pending` - операция в обработке\n"
               "- `cancelled` - операция отменена\n\n"
               "**Параметры пагинации:**\n"
               "- `limit` - количество операций на страницу (по умолчанию: все)\n"
               "- `offset` - смещение от начала списка (по умолчанию: 0)\n\n"
               "**Требования:**\n"
               "- Пользователь должен быть авторизован\n",
    responses={
        200: {
            "description": "Операции реферала успешно получены",
            "content": {
                "application/json": {
                    "example": {
                        "operations": [
                            {
                                "referral_operation_id": "550e8400-e29b-41d4-a716-446655440000",
                                "status": "confirmed",
                                "operation_type": "deposit",
                                "amount": 100.50,
                                "created_at": "2024-01-15T10:30:00"
                            },
                            {
                                "referral_operation_id": "550e8400-e29b-41d4-a716-446655440001",
                                "status": "pending",
                                "operation_type": "withdraw",
                                "amount": 50.25,
                                "created_at": "2024-01-16T14:45:00"
                            }
                        ],
                        "total": 2,
                        "limit": 10,
                        "offset": 0
                    }
                }
            }
        },
        404: {
            "description": "Реферал не найден",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Реферал не найден",
                        "type": "ReferralNotFoundError"
                    }
                }
            }
        }
    }
)
async def get_referral_operations(
    user: UserAuthDep,
    service: ReferralServiceDep,
    pagination: PaginationDep
):
    """
    Получить операции реферала с пагинацией.
    
    Возвращает список всех операций реферального аккаунта пользователя
    с поддержкой пагинации для удобного просмотра истории.
    """
    return await service.get_user_referral_operations(
        user.id, 
        limit=pagination.limit, 
        offset=pagination.offset
    )
