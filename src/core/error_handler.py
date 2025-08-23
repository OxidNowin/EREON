import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.v1.wallet.exceptions import WalletNotFoundError, NetworkNotFoundError, InsufficientFundsError
from api.v1.payment.exceptions import PaymentProcessingError, PaymentLinkError
from api.v1.user.exceptions import EntryCodeUpdateError
from api.v1.auth.exceptions import InvalidEntryCodeError
from api.v1.webhook.exceptions import TransactionAlreadyExistsError
from banking.exceptions import BankApiError, BankTokenError
from banking.providers.alfa.exceptions import AlfaTokenError, AlfaApiError, AlfaRsaSignatureError

logger = logging.getLogger(__name__)


async def wallet_not_found_handler(request: Request, exc: WalletNotFoundError) -> JSONResponse:
    """Обработчик для ошибок wallet модуля"""
    logger.error(f"Wallet error: {exc.message}", extra={"path": request.url.path})
    
    return JSONResponse(
        status_code=404,
        content={
            "error": exc.message,
            "type": exc.__class__.__name__
        }
    )


async def network_not_found_handler(request: Request, exc: NetworkNotFoundError) -> JSONResponse:
    """Обработчик для ошибок: сеть не найдена"""
    logger.error(f"Network not found error: {exc.message}", extra={"path": request.url.path})
    
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.message,
            "type": exc.__class__.__name__
        }
    )


async def insufficient_funds_handler(request: Request, exc: InsufficientFundsError) -> JSONResponse:
    """Обработчик для ошибок недостатка средств"""
    logger.error(f"Insufficient funds error: {exc.message}", extra={"path": request.url.path})
    
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.message,
            "type": exc.__class__.__name__
        }
    )


async def payment_processing_handler(request: Request, exc: PaymentProcessingError) -> JSONResponse:
    """Обработчик для ошибок обработки платежей"""
    logger.error(f"Payment processing error: {exc.message}", extra={"path": request.url.path})
    
    return JSONResponse(
        status_code=502,
        content={
            "error": exc.message,
            "type": exc.__class__.__name__
        }
    )


async def payment_link_handler(request: Request, exc: PaymentLinkError) -> JSONResponse:
    """Обработчик для ошибок получения платежной ссылки"""
    logger.error(f"Payment link error: {exc.message}", extra={"path": request.url.path})
    
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.message,
            "type": exc.__class__.__name__
        }
    )


async def entry_code_update_handler(request: Request, exc: EntryCodeUpdateError) -> JSONResponse:
    """Обработчик для ошибок обновления кода входа"""
    logger.error(f"Entry code update error: {exc.message}", extra={"path": request.url.path})
    
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.message,
            "type": exc.__class__.__name__
        }
    )


async def invalid_entry_code_handler(request: Request, exc: InvalidEntryCodeError) -> JSONResponse:
    """Обработчик для ошибок неверного кода входа"""
    logger.error(f"Invalid entry code error: {exc.message}", extra={"path": request.url.path})
    
    return JSONResponse(
        status_code=401,
        content={
            "error": exc.message,
            "type": exc.__class__.__name__
        }
    )


async def transaction_exists_handler(request: Request, exc: TransactionAlreadyExistsError) -> JSONResponse:
    """Обработчик для ошибок существующих транзакций"""
    logger.error(f"Transaction exists error: {exc.message}", extra={"path": request.url.path})
    
    return JSONResponse(
        status_code=409,
        content={
            "error": exc.message,
            "type": exc.__class__.__name__
        }
    )


async def bank_exception_handler(request: Request, exc: BankApiError) -> JSONResponse:
    """Обработчик для банковских исключений"""
    logger.error(f"Bank API error: {exc.message}", extra={
        "status_code": exc.status_code,
        "response_data": exc.response_data,
        "path": request.url.path
    })
    
    return JSONResponse(
        status_code=exc.status_code or 400,
        content={
            "error": exc.message,
            "type": "BankApiError",
            "details": exc.response_data or {}
        }
    )


async def bank_token_exception_handler(request: Request, exc: BankTokenError) -> JSONResponse:
    """Обработчик для ошибок токенов банка"""
    logger.error(f"Bank token error: {exc.message}", extra={
        "status_code": exc.status_code,
        "response_data": exc.response_data,
        "path": request.url.path
    })
    
    return JSONResponse(
        status_code=exc.status_code or 401,
        content={
            "error": exc.message,
            "type": "BankTokenError",
            "details": exc.response_data or {}
        }
    )


async def alfa_exception_handler(request: Request, exc: AlfaApiError) -> JSONResponse:
    """Обработчик для ошибок Alfa Bank API"""
    logger.error(f"Alfa Bank API error: {exc.message}", extra={
        "path": request.url.path
    })
    
    return JSONResponse(
        status_code=502,
        content={
            "error": exc.message,
            "type": "AlfaApiError"
        }
    )


async def alfa_token_exception_handler(request: Request, exc: AlfaTokenError) -> JSONResponse:
    """Обработчик для ошибок токенов Alfa Bank"""
    logger.error(f"Alfa Bank token error: {exc.message}", extra={
        "path": request.url.path
    })
    
    return JSONResponse(
        status_code=401,
        content={
            "error": exc.message,
            "type": "AlfaTokenError"
        }
    )


async def alfa_rsa_exception_handler(request: Request, exc: AlfaRsaSignatureError) -> JSONResponse:
    """Обработчик для ошибок RSA подписи Alfa Bank"""
    logger.error(f"Alfa Bank RSA signature error: {exc.message}", extra={
        "path": request.url.path
    })
    
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.message,
            "type": "AlfaRsaSignatureError"
        }
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрация всех обработчиков исключений"""
    
    # Модульные исключения
    app.add_exception_handler(WalletNotFoundError, wallet_not_found_handler)
    app.add_exception_handler(NetworkNotFoundError, network_not_found_handler)
    app.add_exception_handler(InsufficientFundsError, insufficient_funds_handler)
    app.add_exception_handler(PaymentProcessingError, payment_processing_handler)
    app.add_exception_handler(PaymentLinkError, payment_link_handler)
    app.add_exception_handler(EntryCodeUpdateError, entry_code_update_handler)
    app.add_exception_handler(InvalidEntryCodeError, invalid_entry_code_handler)
    app.add_exception_handler(TransactionAlreadyExistsError, transaction_exists_handler)
    
    # Банковские исключения
    app.add_exception_handler(BankApiError, bank_exception_handler)
    app.add_exception_handler(BankTokenError, bank_token_exception_handler)
    
    # Alfa Bank исключения
    app.add_exception_handler(AlfaApiError, alfa_exception_handler)
    app.add_exception_handler(AlfaTokenError, alfa_token_exception_handler)
    app.add_exception_handler(AlfaRsaSignatureError, alfa_rsa_exception_handler)
