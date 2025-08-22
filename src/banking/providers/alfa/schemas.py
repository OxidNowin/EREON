from enum import Enum

from pydantic import BaseModel, Field


class AlfaScope(Enum):
    """Доступные scope'ы для Alfa Bank API"""
    SIGNATURE = "signature"
    B2B_SBP = "b2b-sbp"
    OPENID = "openid"


class QRCodeType(Enum):
    """Типы QR-кодов Alfa Bank"""
    ONETIME = "ONETIME"      # Одноразовый QR-код
    REUSABLE = "REUSABLE"    # Многоразовый QR-код


class PaymentStatus(Enum):
    """Статусы платежей Alfa Bank"""
    SENDING_MESSAGE = "SENDING_MESSAGE"
    DRAFT = "DRAFT"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"


class SignatureType(Enum):
    """Типы электронных подписей"""
    KEP = "KEP"  # Квалифицированная электронная подпись
    RSA = "RSA"  # RSA подпись


class ClientInfo(BaseModel):
    """Информация о клиенте для исходящего платежа"""
    b2b_client_id: str = Field(..., description="Идентификатор B2B клиента")
    partner_id: int = Field(..., description="Идентификатор партнёра")
    
    class Config:
        alias_generator = lambda field_name: {
            'b2b_client_id': 'b2bClientId',
            'partner_id': 'partnerId',
        }.get(field_name, field_name)
        populate_by_name = True


class DigestSignature(BaseModel):
    """Электронная подпись по дайджесту документа"""
    base64_encoded: str = Field(..., description="Значение электронной подписи в Base64")
    certificate_uuid: str | None = Field(None, description="Серийный номер сертификата")
    signature_type: SignatureType = Field(..., description="Тип электронной подписи")
    poa_number: str | None = Field(None, description="Номер машиночитаемой доверенности")
    
    class Config:
        alias_generator = lambda field_name: {
            'base64_encoded': 'base64Encoded',
            'certificate_uuid': 'certificateUuid',
            'signature_type': 'signatureType',
            'poa_number': 'poaNumber',
        }.get(field_name, field_name)
        populate_by_name = True
        use_enum_values = True


class PaymentRequest(BaseModel):
    """Запрос на выполнение исходящего платежа"""
    client: ClientInfo = Field(..., description="Контекст клиента")
    qrc_id: str = Field(..., description="Идентификатор платёжной ссылки")
    payer_account: str = Field(..., description="Счёт списания")
    amount: int = Field(..., ge=1, description="Сумма к зачислению в копейках")
    payment_purpose: str = Field(..., max_length=210, description="Назначение платежа")
    take_tax: bool = Field(..., description="Информация о взимании НДС")
    tax_amount: int | None = Field(None, ge=0, description="Сумма налога в копейках")
    digest_signatures: list[DigestSignature] = Field(default_factory=list, description="Электронные подписи")
    
    class Config:
        alias_generator = lambda field_name: {
            'qrc_id': 'qrcId',
            'payer_account': 'payerAccount',
            'payment_purpose': 'paymentPurpose',
            'take_tax': 'takeTax',
            'tax_amount': 'taxAmount',
            'digest_signatures': 'digestSignatures',
        }.get(field_name, field_name)
        populate_by_name = True


class PaymentResponse(BaseModel):
    """Ответ на запрос выполнения исходящего платежа"""
    outgoing_payment_id: str = Field(..., description="Идентификатор платежа в СБП B2B")
    qrc_id: str = Field(..., description="Идентификатор платёжной ссылки")
    status: PaymentStatus = Field(..., description="Статус платежа")
    commission: int = Field(..., description="Сумма комиссии в копейках")
    
    class Config:
        alias_generator = lambda field_name: {
            'outgoing_payment_id': 'outgoingPaymentId',
            'qrc_id': 'qrcId',
        }.get(field_name, field_name)
        populate_by_name = True


class PaymentLinkData(BaseModel):
    """Данные по зарегистрированной платёжной ссылке Alfa Bank"""
    
    qrc_id: str = Field(..., description="Идентификатор платёжной ссылки")
    qrc_type: QRCodeType = Field(..., description="Тип QR-кода")
    legal_id: str = Field(..., description="Идентификатор юридического лица")
    legal_name: str = Field(..., description="Наименование юридического лица")
    member_id: str = Field(..., description="Идентификатор участника")
    brand_name: str = Field(..., description="Название бренда")
    payee_account: str | None = Field(None, description="Счёт получателя")
    merchant_id: str = Field(..., description="Идентификатор мерчанта")
    amount: int = Field(..., description="Сумма платежа (в копейках)")
    payment_purpose: str = Field(" ", description="Назначение платежа")
    address: str = Field(..., description="Адрес")
    mcc: str = Field(..., description="Код категории мерчанта")
    fraud_score: str | None = Field(None, description="Скоринг мошенничества")
    inn: str | None = Field(None, description="ИНН")
    redirect_url: str | None = Field(None, description="URL переадресации")
    agent_id: str | None = Field(None, description="Идентификатор агента")
    take_tax: bool = Field(..., description="Брать налог")
    tax_amount: int | None = Field(None, description="Сумма налога (в копейках)")
    uip: str | None = Field(None, description="УИП (уникальный идентификатор платежа)")
    
    class Config:
        alias_generator = lambda field_name: {
            'qrc_id': 'qrcId',
            'qrc_type': 'qrcType', 
            'legal_id': 'legalId',
            'legal_name': 'legalName',
            'member_id': 'memberId',
            'brand_name': 'brandName',
            'payee_account': 'payeeAccount',
            'merchant_id': 'merchantId',
            'payment_purpose': 'paymentPurpose',
            'fraud_score': 'fraudScore',
            'redirect_url': 'redirectUrl',
            'agent_id': 'agentId',
            'take_tax': 'takeTax',
            'tax_amount': 'taxAmount',
        }.get(field_name, field_name)
        
        populate_by_name = True


class PaymentStatusResponse(BaseModel):
    """Статус исходящего платежа Alfa Bank"""
    
    outgoing_payment_id: str = Field(..., description="Идентификатор платежа в СБП B2B")
    qrc_id: str = Field(..., description="Идентификатор платёжной ссылки")
    status: PaymentStatus = Field(..., description="Статус платежа")
    
    class Config:
        alias_generator = lambda field_name: {
            'outgoing_payment_id': 'outgoingPaymentId',
            'qrc_id': 'qrcId',
        }.get(field_name, field_name)
        
        populate_by_name = True 
    