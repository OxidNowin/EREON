from uuid import UUID

from fastapi import APIRouter

from api.v1.operation.schemas import OperationBase
from api.v1.wallet.dependencies import WalletServiceDep
from api.v1.wallet.schemas import WalletResponse, WalletCurrencyList, WithdrawRequest
from api.v1.auth.dependencies import UserAuthDep

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get(
    "/currencies", 
    response_model=WalletCurrencyList,
    summary="Получить список поддерживаемых валют",
    description="Возвращает список всех поддерживаемых криптовалют для кошельков.\n\n"
               "**Возвращаемая информация:**\n"
               "- Список доступных валют (например, USDT, BTC, ETH)\n\n"
               "**Особенности:**\n"
               "- Эндпоинт не требует авторизации\n"
               "- Возвращает список валют\n"
               "**Использование:**\n"
               "- Для отображения доступных валют в интерфейсе\n",
    responses={
        200: {
            "description": "Список валют успешно получен",
            "content": {
                "application/json": {
                    "example": {
                        "currencies": ["USDT", "BTC", "ETH"]
                    }
                }
            }
        }
    }
)
def get_currencies(wallet_service: WalletServiceDep) -> WalletCurrencyList:
    """
    Получить список поддерживаемых валют.
    
    Возвращает кэшированный список всех криптовалют,
    которые поддерживаются системой для создания кошельков.
    """
    return wallet_service.get_currencies()


@router.get(
    "", 
    response_model=list[WalletResponse],
    summary="Получить все кошельки пользователя",
    description="Возвращает список всех кошельков, принадлежащих авторизованному пользователю.\n\n"
               "**Возвращаемая информация:**\n"
               "- Список кошельков с детальной информацией\n"
               "- Для каждого кошелька: ID, валюта, баланс, адреса\n\n"
               "**Требования:**\n"
               "- Пользователь должен быть авторизован\n"
               "**Особенности:**\n"
               "- Возвращает только кошельки текущего пользователя\n"
               "- Кошельки группируются по валютам\n"
               "- Адреса автоматически определяются по сети",
    responses={
        200: {
            "description": "Список кошельков успешно получен",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "wallet_id": "550e8400-e29b-41d4-a716-446655440000",
                            "currency": "USDT",
                            "balance": "1000.50",
                            "addresses": [
                                {
                                    "network": "TRC20",
                                    "address": "TQn9Y2khDD95J42FQtQTdwVVRqQjKCz9JQ"
                                }
                            ]
                        }
                    ]
                }
            }
        },
        404: {
            "description": "Кошельки не найдены",
            "content": {
                "application/json": {
                    "example": {
                        "error": "No wallets found for user with telegram_id 123456789",
                        "type": "WalletNotFoundError"
                    }
                }
            }
        }
    }
)
async def get_all_wallets(
    user: UserAuthDep,
    wallet_service: WalletServiceDep
):
    """
    Получить все кошельки пользователя.
    
    Возвращает список всех кошельков, принадлежащих авторизованному пользователю,
    с информацией о балансе, валюте и адресах для каждой криптовалюты.
    """
    return await wallet_service.get_wallets(user.id)


@router.get(
    "/{wallet_id}", 
    response_model=WalletResponse,
    summary="Получить конкретный кошелек",
    description="Возвращает детальную информацию о конкретном кошельке по его ID.\n\n"
               "**Возвращаемая информация:**\n"
               "- ID кошелька\n"
               "- Тип криптовалюты\n"
               "- Текущий баланс\n"
               "- Список адресов для пополнения\n\n"
               "**Параметры пути:**\n"
               "- `wallet_id` - уникальный идентификатор кошелька (UUID)\n\n"
               "**Требования:**\n"
               "- Пользователь должен быть авторизован\n"
               "- Кошелек должен принадлежать авторизованному пользователю\n\n"
               "**Особенности:**\n",
    responses={
        200: {
            "description": "Информация о кошельке успешно получена",
            "content": {
                "application/json": {
                    "example": {
                        "wallet_id": "550e8400-e29b-41d4-a716-446655440000",
                        "currency": "USDT",
                        "balance": "1000.50",
                        "addresses": [
                            {
                                "network": "TRC20",
                                "address": "TQn9Y2khDD95J42FQtQTdwVVRqQjKCz9JQ"
                            }
                        ]
                    }
                }
            }
        },
        404: {
            "description": "Кошелек не найден",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Wallet with id 550e8400-e29b-41d4-a716-446655440000 not found",
                        "type": "WalletNotFoundError"
                    }
                }
            }
        }
    }
)
async def get_wallet(
        user: UserAuthDep,
        wallet_id: UUID,
        wallet_service: WalletServiceDep
):
    """
    Получить конкретный кошелек.
    
    Возвращает детальную информацию о кошельке по его ID,
    включая баланс, валюту и адреса для пополнения.
    """
    return await wallet_service.get_wallet(wallet_id)


@router.post(
    "/{wallet_id}/withdrawal", 
    response_model=OperationBase,
    summary="Вывести средства с кошелька",
    description="Позволяет пользователю вывести криптовалюту с кошелька на указанный адрес.\n\n"
               "**Процесс вывода:**\n"
               "1. Система проверяет достаточность средств на кошельке\n"
               "2. Рассчитывается комиссия сети для указанного адреса\n"
               "3. Создается операция вывода средств\n"
               "4. Средства отправляются на указанный адрес через криптопроцессинг\n\n"
               "**Параметры пути:**\n"
               "- `wallet_id` - уникальный идентификатор кошелька (UUID)\n\n"
               "**Параметры тела запроса:**\n"
               "- `address` - адрес для вывода средств (автоматически определяется сеть)\n"
               "- `amount` - сумма для вывода (в основной валюте кошелька)\n\n"
               "**Требования:**\n"
               "- Пользователь должен быть авторизован\n"
               "- На кошельке должно быть достаточно средств (сумма + комиссия сети)\n"
               "- Адрес должен поддерживаться системой\n\n"
               "**Особенности:**\n"
               "- Комиссия сети рассчитывается автоматически\n"
               "- Общая сумма списания = сумма вывода + комиссия сети\n"
               "- Операция создается со статусом CONFIRMED при успешном выводе",
    responses={
        200: {
            "description": "Средства успешно выведены",
            "content": {
                "application/json": {
                    "example": {
                        "operation_id": "550e8400-e29b-41d4-a716-446655440000",
                        "wallet_id": "550e8400-e29b-41d4-a716-446655440001",
                        "status": "CONFIRMED",
                        "operation_type": "WITHDRAW",
                        "amount": "100.00",
                        "fee": "1.00",
                        "total_amount": "101.00",
                        "created_at": "2024-01-15T10:30:00"
                    }
                }
            }
        },
        400: {
            "description": "Ошибка вывода средств",
            "content": {
                "application/json": {
                    "examples": {
                        "InsufficientFunds": {
                            "summary": "Недостаточно средств",
                            "value": {
                                "error": "Insufficient funds. Required: 101.00, available: 100.00",
                                "type": "InsufficientFundsError"
                            }
                        },
                        "NetworkFeeError": {
                            "summary": "Ошибка получения комиссии сети",
                            "value": {
                                "error": "Failed to get network fee for address TQn9Y2khDD95J42FQtQTdwVVRqQjKCz9JQ",
                                "type": "NetworkFeeError"
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "Кошелек не найден",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Wallet with id 550e8400-e29b-41d4-a716-446655440000 not found for user 123456789",
                        "type": "WalletNotFoundError"
                    }
                }
            }
        },
        422: {
            "description": "Ошибка валидации данных",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Validation error",
                        "type": "RequestValidationError",
                        "details": [
                            {
                                "loc": ["body", "amount"],
                                "msg": "Input should be greater than 0",
                                "type": "value_error.number.not_gt"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def withdraw_funds(
        wallet_id: UUID,
        data: WithdrawRequest,
        user: UserAuthDep,
        wallet_service: WalletServiceDep
):
    """
    Вывести средства с кошелька.
    
    Позволяет авторизованному пользователю вывести криптовалюту
    с указанного кошелька на заданный адрес с автоматическим расчетом комиссии сети.
    """
    return await wallet_service.withdraw_funds(wallet_id, user.id, data)
