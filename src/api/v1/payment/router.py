from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, status, Path

from api.v1.payment.schemas import SbpPaymentCreate, SbpPaymentResponse
from api.v1.payment.dependencies import PaymentServiceDep
from api.v1.auth.dependencies import UserAuthDep

router = APIRouter(tags=["Payment"])


@router.post(
    "/wallet/{wallet_id}/one-pay",
    status_code=status.HTTP_200_OK,
    response_model=SbpPaymentResponse,
    summary="Создать SBP платеж",
    description="Создает новый SBP платеж для вывода средств с кошелька.\n\n"
                "**Процесс обработки:**\n"
                "1. Валидация кошелька и проверка принадлежности пользователю\n"
                "2. Получение данных платежной ссылки от Альфа-Банка\n"
                "3. Проверка достаточности средств на кошельке\n"
                "4. Обработка платежа через банковский API\n"
                "5. Создание операции и записи SBP платежа\n"
                "6. Мониторинг статуса платежа (до 15 секунд)\n\n"
                "**Требования:**\n"
                "- Пользователь должен быть авторизован\n"
                "- На кошельке должно быть достаточно средств\n"
                "- SBP URL должен быть валидным (qr.nspk.ru)\n\n",
    responses={
        200: {
            "description": "SBP платеж успешно создан",
            "content": {
                "application/json": {
                    "example": {
                        "sbp_payment_id": "123e4567-e89b-12d3-a456-426614174000",
                        "rub_amount": 10000,
                        "fee_rub": 100,
                        "total_amount_rub": 10100,
                        "crypto_amount": "0.001",
                        "fee_crypto": "0.00001",
                        "total_amount_crypto": "0.00101",
                        "exchange": "100000",
                        "status": "CONFIRMED",
                        "created_at": "2024-01-01T12:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Ошибка валидации данных",
            "content": {
                "application/json": {
                    "example": {
                        "error": "SBP URL должен использовать хост qr.nspk.ru",
                        "type": "ValidationError"
                    }
                }
            }
        },
        404: {
            "description": "Кошелек не найден",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Wallet with id 123e4567-e89b-12d3-a456-426614174000 not found for user 456e7890-e89b-12d3-a456-426614174000",
                        "type": "WalletNotFoundError"
                    }
                }
            }
        },
        409: {
            "description": "Недостаточно средств",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Insufficient funds. Required: 0.001, available: 0.0005",
                        "type": "InsufficientFundsError"
                    }
                }
            }
        },
        502: {
            "description": "Ошибка внешнего сервиса",
            "content": {
                "application/json": {
                    "examples": {
                        "payment_link_error": {
                            "summary": "Ошибка получения данных платежной ссылки",
                            "value": {
                                "error": "Getting payment link failed",
                                "type": "PaymentLinkError"
                            }
                        },
                        "payment_processing_error": {
                            "summary": "Ошибка обработки платежа",
                            "value": {
                                "error": "Payment processing failed",
                                "type": "PaymentProcessingError"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def create_sbp_payment(
    user: UserAuthDep,
    payment_data: SbpPaymentCreate,
    service: PaymentServiceDep,
    wallet_id: Annotated[UUID, Path(..., description="ID кошелька")],
) -> SbpPaymentResponse:
    """Создать новый SBP платеж"""
    return await service.create_sbp_payment(user.id, wallet_id, payment_data)
