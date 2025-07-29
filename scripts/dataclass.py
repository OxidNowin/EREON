from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List


class RequestType(str, Enum):
    issueRsaCertificate = "issueRsaCertificate"
    activationRsaCertificate = "activationRsaCertificate"
    currentSignTypeRsa = "currentSignTypeRsa"
    currentSignTypeQes = "currentSignTypeQes"
    switchRsaCertificate = "switchRsaCertificate"
    reissueRsaCertificate = "reissueRsaCertificate"
    revocationRsaCertificate = "revocationRsaCertificate"


class RequestStatus(str, Enum):
    CREATED = "CREATED"
    SIGNED = "SIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"
    FAILED = "FAILED"


@dataclass
class ResponseRsaCertificateBase:
    id: str
    type: str
    status: str
    creator: str
    createdDate: str


@dataclass
class ResponseActivationRsaCertificate(ResponseRsaCertificateBase):
    ...


@dataclass
class ResponseIssueRsaCertificate(ResponseRsaCertificateBase):
    ...


@dataclass
class OperationResponse:
    id: str
    requestId: str
    requestType: RequestType


@dataclass
class BaseGetRequestObject:
    id: str
    type: RequestType
    status: RequestStatus
    creator: str
    createdDate: str
    finishedDate: str


@dataclass
class CertificateOwner:
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    fullName: Optional[str] = None
    country: Optional[str] = None
    email: Optional[str] = None


@dataclass
class ResultsRequestRsaCertificate:
    owner: Optional[str] = None
    notAfter: Optional[str] = None
    notBefore: Optional[str] = None
    serialNumber: Optional[str] = None
    sendDate: Optional[str] = None
    executionDate: Optional[str] = None
    thumbprint: Optional[str] = None
    dn: Optional[CertificateOwner] = None
    issuedCertificateId: Optional[str] = None
    caRequestId: Optional[int] = None


@dataclass
class ResultsActivateRsaCertificateObject:
    userSignMethodType: Optional[str] = None
    userSignMethodStatus: Optional[str] = None


@dataclass
class RequestIssueRsaCertificateObject(BaseGetRequestObject):
    results: Optional[ResultsRequestRsaCertificate] = None


@dataclass
class RequestActivateRsaCertificateObject(BaseGetRequestObject):
    results: Optional[ResultsActivateRsaCertificateObject] = None


@dataclass
class RequestSwitchRsaCertificateObject(RequestIssueRsaCertificateObject):
    ...


@dataclass
class GetRequestResponse:
    requestIssueRsaCertificate: Optional[list[RequestIssueRsaCertificateObject]] = None
    requestActivateRsaCertificate: Optional[list[RequestActivateRsaCertificateObject]] = None
    requestCurrentSignTypeRsa: Optional[list[BaseGetRequestObject]] = None
    requestCurrentSignTypeQes: Optional[list[BaseGetRequestObject]] = None
    requestSwitchRsaCertificate: Optional[list[RequestSwitchRsaCertificateObject]] = None
    requestRevocationRsaCertificate: Optional[list[BaseGetRequestObject]] = None


@dataclass
class JWTHeader:
    """Заголовок JWT токена"""
    kid: Optional[str] = None
    typ: Optional[str] = None
    alg: Optional[str] = None


@dataclass
class JWTClaims:
    """Claims (payload) JWT токена"""
    sub: Optional[str] = None
    aud: Optional[str] = None
    iss: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    jti: Optional[str] = None
    scope_services: Optional[List[str]] = None
    scope_claims: Optional[List[str]] = None

    @property
    def expires_at(self) -> Optional[datetime]:
        """Время истечения токена как datetime"""
        if self.exp:
            return datetime.fromtimestamp(self.exp)
        return None

    @property
    def issued_at(self) -> Optional[datetime]:
        """Время выдачи токена как datetime"""
        if self.iat:
            return datetime.fromtimestamp(self.iat)
        return None

    @property
    def is_expired(self) -> bool:
        """Проверяет, истек ли токен"""
        if not self.exp:
            return True
        return datetime.now().timestamp() > self.exp

    @property
    def time_remaining(self) -> Optional[int]:
        """Оставшееся время жизни токена в секундах"""
        if not self.exp:
            return None
        remaining = self.exp - datetime.now().timestamp()
        return int(remaining) if remaining > 0 else 0


@dataclass
class JWTToken:
    """Полная информация о JWT токене"""
    token: str
    header: JWTHeader
    claims: JWTClaims
    is_signature_valid: bool = False
    verification_error: Optional[str] = None