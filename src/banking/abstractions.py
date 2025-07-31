from dataclasses import dataclass
from typing import Protocol, TypeVar

# TypeVar для scope'ов разных банков
ScopeType = TypeVar('ScopeType')


@dataclass
class PaymentBase:
    payment_id: str
    status: str
    commission: int


@dataclass  
class PaymentResult(PaymentBase):
    """Результат платежа"""
    amount: int


@dataclass
class PaymentStatus(PaymentBase):
    """Статус платежа"""
    ...


@dataclass
class PaymentLink:
    qrc_id: str
    amount: int
    payment_purpose: str
    take_tax: bool
    tax_amount: int | None = None


class ITokenService(Protocol[ScopeType]):
    """Общий интерфейс для сервиса управления токенами доступа"""
    
    async def get_access_token(self, scope: ScopeType) -> str:
        """Получить действующий токен доступа для указанного scope"""
        ...
    
    async def invalidate_token(self, scope: ScopeType) -> None:
        """Инвалидировать токен для указанного scope"""
        ...


class IBankPaymentClient(Protocol):
    """Интерфейс для клиентов банковских API"""
    
    async def process_payment(self, payment_link: PaymentLink) -> PaymentResult:
        """Обработать платеж по QR-коду"""
        ...

    async def get_payment_link_data(self, qrc_id: str) -> PaymentLink:
        """Получить информацию по платежу"""
        ...

    async def get_payment_status(self, payment_id: str) -> PaymentStatus | None:
        """Получить статус платежа"""
        ...
    
    async def close(self) -> None:
        """Закрыть соединение"""
        ...
