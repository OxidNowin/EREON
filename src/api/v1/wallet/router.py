from uuid import UUID

from fastapi import APIRouter

from api.v1.wallet.dependencies import WalletServiceDep
from api.v1.wallet.schemas import WalletResponse, WalletCurrencyList
from api.v1.auth.dependencies import UserAuthDep

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("/currencies", response_model=WalletCurrencyList)
def get_currencies(wallet_service: WalletServiceDep) -> WalletCurrencyList:
    return wallet_service.get_currencies()


@router.get("", response_model=list[WalletResponse])
async def get_all_wallets(
    user: UserAuthDep,
    wallet_service: WalletServiceDep
) -> list[WalletResponse]:
    return await wallet_service.get_wallets(user.id)


@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet(
        user: UserAuthDep,
        wallet_id: UUID,
        wallet_service: WalletServiceDep
) -> WalletResponse:
    return await wallet_service.get_wallet(wallet_id)
