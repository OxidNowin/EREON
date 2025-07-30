import asyncio
import base64
import tempfile
from logging import getLogger
from pathlib import Path

import aiohttp

from core.config import settings
from banking.abstractions import ITokenService, PaymentResult, PaymentStatus
from banking.providers.alfa.exceptions import AlfaApiError, AlfaRsaSignatureError
from banking.providers.alfa.schemas import (
    PaymentLinkData, 
    PaymentStatusResponse,
    PaymentRequest,
    PaymentResponse,
    ClientInfo,
    DigestSignature,
    SignatureType,
    AlfaScope,
)

logger = getLogger(__name__)


class AlfaClient:
    """Клиент для работы с Alfa Bank API"""

    client_info = ClientInfo(
        b2b_client_id=settings.alfa_b2b_client_id,
        partner_id=settings.alfa_partner_id
    )
    CERT_PATH = settings.alfa_rsa_cert_path
    PRIVATE_KEY_PATH = settings.alfa_rsa_private_key_path


    def __init__(self, token_service: ITokenService[AlfaScope]):
        self._token_service = token_service
        self._session: aiohttp.ClientSession | None = None
    
    def _get_session(self) -> aiohttp.ClientSession:
        """Получить или создать HTTP сессию"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self) -> None:
        """Закрыть HTTP сессию"""
        if self._session and not self._session.closed:
            await self._session.close()

    @staticmethod
    def _create_digest(payment_request: PaymentRequest) -> str:
        """
        Создать дайджест для подписания согласно требованиям Alfa Bank.
        
        Требования:
        - UTF-8 кодировка
        - Поля отсортированы по алфавиту (A-Z)
        - Разделитель строк \r\n (Windows format)
        - Последняя строка без перевода строки
        - Только поля, которые передаются в запросе
        """
        digest_lines = [
            f"amount={payment_request.amount}",
            f"b2bClientId={payment_request.client.b2b_client_id}",
            f"partnerId={payment_request.client.partner_id}",
            f"payerAccount={payment_request.payer_account}",
            f"paymentPurpose={payment_request.payment_purpose}",
            f"qrcId={payment_request.qrc_id}",
            f"takeTax={'true' if payment_request.take_tax else 'false'}"
        ]
        
        if payment_request.tax_amount is not None:
            digest_lines.append(f"taxAmount={payment_request.tax_amount}")
        
        return "\r\n".join(digest_lines)

    async def _create_signature(self, digest: str) -> DigestSignature:
        """
        Создать фейковую подпись для тестирования.
        """
        base64_encoded = await self.sign_pkcs7_detached(digest)
        
        return DigestSignature(
            base64_encoded=base64_encoded,
            certificate_uuid=settings.alfa_rsa_serial_number,
            signature_type=SignatureType.RSA,
            poa_number=None
        )

    async def get_payment_link_data(self, qrc_id: str) -> PaymentLinkData:
        """Получить данные по зарегистрированной платёжной ссылке"""
        token = await self._token_service.get_access_token(scope=AlfaScope.B2B_SBP)
        
        url = f"{settings.alfa_base_url}/api/sbp/jp/v1/payment-urls/{qrc_id}/data"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        session = self._get_session()
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                try:
                    error_data = await resp.json()
                except Exception:
                    error_data = {}
                logger.error("Ошибка получения данных платёжной ссылки %s: %s, %s", qrc_id, resp.status, error_data)
                raise AlfaApiError("Не удалось получить данные по платежной ссылке")
            
            response_data = await resp.json()
        
        return PaymentLinkData(**response_data)

    async def process_payment(self, qrc_id: str) -> PaymentResult:
        """Обработать платеж по QR-коду"""
        # Получаем данные по платежной ссылке
        payment_link_data = await self.get_payment_link_data(qrc_id)
        
        # Выполняем платеж
        token = await self._token_service.get_access_token(scope=AlfaScope.B2B_SBP)
    
        payment_request = PaymentRequest(
            client=self.client_info,
            qrc_id=payment_link_data.qrc_id,
            payer_account=settings.alfa_payer_account,
            amount=payment_link_data.amount,
            payment_purpose=payment_link_data.payment_purpose,
            take_tax=payment_link_data.take_tax,
            tax_amount=payment_link_data.tax_amount,
        )
        
        digest = self._create_digest(payment_request)
        signature = await self._create_signature(digest)
        payment_request.digest_signatures.append(signature)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        session = self._get_session()
        async with session.post(
            url=f"{settings.alfa_base_url}/api/sbp/jp/v1/outgoing-payments/one-pay",
            json=payment_request.model_dump(by_alias=True), 
            headers=headers
        ) as resp:
            if resp.status != 201:
                try:
                    error_data = await resp.json()
                except Exception:
                    error_data = {}
                raise AlfaApiError(
                    message=f"Ошибка выполнения исходящего платежа: {qrc_id}",
                    status_code=resp.status,
                    response_data=error_data
                )
            
            response_data = await resp.json()
        
        payment_response = PaymentResponse(**response_data)

        return PaymentResult(
            payment_id=payment_response.outgoing_payment_id,
            status=payment_response.status.value,
            amount=payment_link_data.amount,
            commission=payment_response.commission
        )

    async def get_payment_status(self, payment_id: str) -> PaymentStatus | None:
        """Получить статус исходящего платежа"""
        
        token = await self._token_service.get_access_token(scope=AlfaScope.B2B_SBP)
        
        url = f"{settings.alfa_base_url}/api/sbp/jp/v1/outgoing-payments/{payment_id}/status"
        params = {"b2bClientId": settings.alfa_b2b_client_id}
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        session = self._get_session()
        async with session.get(url, params=params, headers=headers) as resp:
            if resp.status != 200:
                try:
                    error_data = await resp.json()
                except Exception:
                    error_data = {}
                logger.error(
                    "Ошибка получения статуса исходящего платежа %s: %s, %s",
                    payment_id, resp.status, error_data
                )
                return None
            
            response_data = await resp.json()

        payment_response = PaymentStatusResponse(**response_data)

        return PaymentStatus(
            payment_id=payment_response.outgoing_payment_id,
            status=payment_response.status.value,
            commission=payment_response.commission
        )

    async def sign_pkcs7_detached(self, digest_text: str) -> str:
        """
        Асинхронно подписывает дайджест PKCS#7 Detached подписью через openssl.
        Возвращает base64-подпись.
        """

        # Создаем временные файлы
        with tempfile.TemporaryDirectory() as tmpdir:
            digest_file = Path(tmpdir) / "digest.txt"
            signature_file = Path(tmpdir) / "signature.p7s"

            # Сохраняем дайджест
            digest_file.write_text(digest_text, encoding="utf-8")

            # Подготовка команды openssl
            cmd = [
                "openssl", "smime", "-sign",
                "-in", str(digest_file),
                "-signer", self.CERT_PATH,
                "-inkey", self.PRIVATE_KEY_PATH,
                "-outform", "DER",
                "-binary",
                "-noattr",
                "-out", str(signature_file),
            ]

            # Асинхронно вызываем OpenSSL
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise AlfaRsaSignatureError()

            # Читаем результат и кодируем в base64
            signature_der = signature_file.read_bytes()
            signature_b64 = base64.b64encode(signature_der).decode("ascii")

            return signature_b64
