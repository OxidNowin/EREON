from pydantic import BaseModel


class ApiKeyRefreshResponse(BaseModel):
    newApiKey: str
    message: str


class ClientRegistrationResponse(BaseModel):
    trxAddress: str
    message: str


class WebhookRegistrationResponse(BaseModel):
    message: str
