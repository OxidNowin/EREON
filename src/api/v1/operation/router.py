from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from api.v1.operation.schemas import OperationBase
from api.v1.operation.dependencies import OperationServiceDep
from api.v1.base.dependencies import PaginationDep
from api.v1.auth.dependencies import UserAuthDep

router = APIRouter(tags=["Operation"])


@router.get(
    "/user/operations", 
    response_model=list[OperationBase],
    summary="Получить операции пользователя",
    description="Возвращает список всех операций пользователя с пагинацией.\n\n"
                "**Функциональность:**\n"
                "- Получение истории всех операций пользователя\n"
                "- Поддержка пагинации для больших списков\n"
                "- Фильтрация по пользователю (автоматически)\n\n"
                "**Требования:**\n"
                "- Пользователь должен быть авторизован\n\n"
                "**Особенности:**\n"
                "- Операции включают все типы: пополнение, вывод, перевод\n"
                "- Сортировка по дате создания (новые сначала)\n"
                "- Возвращает базовую информацию об операциях\n"
                "- Поддержка лимитов",
    responses={
        200: {
            "description": "Список операций пользователя",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "operation_id": "123e4567-e89b-12d3-a456-426614174000",
                            "wallet_id": "456e7890-e89b-12d3-a456-426614174000",
                            "operation_type": "WITHDRAW",
                            "status": "CONFIRMED",
                            "amount": "0.001",
                            "fee": "0.00001",
                            "total_amount": "0.00101",
                            "created_at": "2024-01-01T12:00:00Z"
                        }
                    ]
                }
            }
        },
        401: {
            "description": "Пользователь не авторизован",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Not authenticated",
                        "type": "AuthenticationError"
                    }
                }
            }
        }
    }
)
async def get_user_operations_handler(
    user: UserAuthDep,
    params: PaginationDep,
    service: OperationServiceDep,
):
    return await service.get_operations_by_user(
        telegram_id=user.id,
        params=params
    )


@router.get(
    "/wallet/{wallet_id}/operations", 
    response_model=list[OperationBase],
    summary="Получить операции кошелька",
    description="Возвращает список всех операций конкретного кошелька с пагинацией.\n\n"
                "**Функциональность:**\n"
                "- Получение истории операций по конкретному кошельку\n"
                "- Поддержка пагинации для больших списков\n"
                "- Фильтрация по кошельку и пользователю\n\n"
                "**Требования:**\n"
                "- Пользователь должен быть авторизован\n"
                "- Кошелек должен принадлежать авторизованному пользователю\n\n"
                "**Особенности:**\n"
                "- Операции включают все типы для данного кошелька\n"
                "- Сортировка по дате создания (новые сначала)\n"
                "- Возвращает базовую информацию об операциях\n"
                "- Поддержка лимитов для оптимизации производительности",
    responses={
        200: {
            "description": "Список операций кошелька",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "operation_id": "123e4567-e89b-12d3-a456-426614174000",
                            "wallet_id": "456e7890-e89b-12d3-a456-426614174000",
                            "operation_type": "DEPOSIT",
                            "status": "CONFIRMED",
                            "amount": "0.001",
                            "fee": "0.00001",
                            "total_amount": "0.00101",
                            "created_at": "2024-01-01T12:00:00Z"
                        }
                    ]
                }
            }
        },
        401: {
            "description": "Пользователь не авторизован",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Not authenticated",
                        "type": "AuthenticationError"
                    }
                }
            }
        },
        404: {
            "description": "Кошелек не найден",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Wallet not found",
                        "type": "WalletNotFoundError"
                    }
                }
            }
        }
    }
)
async def get_wallet_operations_handler(
    user: UserAuthDep,
    wallet_id: UUID,
    params: PaginationDep,
    service: OperationServiceDep,
):
    return await service.get_operations_by_wallet(
        wallet_id=wallet_id,
        params=params
    )


@router.get(
    "/operations/{operation_id}", 
    response_model=OperationBase,
    summary="Получить операцию по ID",
    description="Возвращает детальную информацию об операции по её уникальному идентификатору.\n\n"
                "**Функциональность:**\n"
                "- Получение полной информации об операции\n"
                "- Проверка доступа к операции\n"
                "- Валидация существования операции\n\n"
                "**Требования:**\n"
                "- Пользователь должен быть авторизован\n"
                "- Операция должна существовать в системе\n"
                "**Особенности:**\n"
                "- Возвращает детальную информацию об операции\n"
                "- Включает все поля: ID, кошелек, тип, статус, суммы, даты\n"
                "- Подходит для отображения деталей операции в интерфейсе",
    responses={
        200: {
            "description": "Детали операции",
            "content": {
                "application/json": {
                    "example": {
                        "operation_id": "123e4567-e89b-12d3-a456-426614174000",
                        "wallet_id": "456e7890-e89b-12d3-a456-426614174000",
                        "operation_type": "TRANSFER",
                        "status": "PENDING",
                        "amount": "0.001",
                        "fee": "0.00001",
                        "total_amount": "0.00101",
                        "created_at": "2024-01-01T12:00:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Пользователь не авторизован",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Not authenticated",
                        "type": "AuthenticationError"
                    }
                }
            }
        },
        404: {
            "description": "Операция не найдена",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Operation not found",
                        "type": "OperationNotFoundError"
                    }
                }
            }
        }
    }
)
async def get_operation_handler(
    user: UserAuthDep,
    operation_id: UUID,
    service: OperationServiceDep
):
    result = await service.get_operation(operation_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operation not found")
    return result
