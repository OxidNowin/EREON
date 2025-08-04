from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, HttpUrl


class SbpPaymentCreate(BaseModel):
    sbp_url: HttpUrl = Field(..., description="URL для SBP платежа")
    exchange: Decimal = Field(..., description="Курс обмена")

    @classmethod
    @field_validator('sbp_url', mode='after')
    def validate_sbp_url(cls, v: HttpUrl) -> HttpUrl:
        if v.host != 'qr.nspk.ru':
            raise ValueError("SBP URL должен использовать хост qr.nspk.ru")
        
        # Проверяем путь (должен содержать QR_ID)
        path_parts = v.path.strip('/').split('/')
        if not path_parts or not path_parts[0]:
            raise ValueError("SBP URL должен содержать QR_ID в пути")
        
        qr_id = path_parts[0]
        if len(qr_id) > 32:
            raise ValueError("QR_ID не может быть длиннее 32 символов")
        
        return v

    def get_qr_id(self) -> str:
        """Извлечь QR_ID из SBP URL"""
        return self.sbp_url.path.strip('/').split('/')[0]


class SbpPaymentResponse(BaseModel):
    sbp_payment_id: UUID = Field(..., description="ID SBP платежа")
    rub_amount: int = Field(..., description="Сумма в копейках")
    fee_rub: int = Field(..., description="Комиссия в копейках")
    total_amount_rub: int = Field(..., description="Общая сумма в копейках")
    crypto_amount: Decimal = Field(..., description="Сумма в криптовалюте")
    fee_crypto: Decimal = Field(..., description="Комиссия в криптовалюте")
    total_amount_crypto: Decimal = Field(..., description="Общая сумма в криптовалюте")
    currency: str = Field(..., description="Валюта")
    exchange: Decimal = Field(..., description="Курс обмена")
    status: str = Field(..., description="Статус платежа")
    created_at: str = Field(..., description="Дата создания")
