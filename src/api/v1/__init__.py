from api.v1.auth.router import router as auth_router
from api.v1.user.router import router as user_router
from api.v1.wallet.router import router as wallet_router
from api.v1.webhook.router import router as webhook_router
from api.v1.operation.router import router as operation_router
from api.v1.payment.router import router as payment_router


__all__ = [
    'auth_router',
    'user_router',
    'wallet_router',
    'webhook_router',
    'operation_router',
    'payment_router',
]