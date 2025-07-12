from uuid import UUID

from fastapi import APIRouter

from api.v1.base.dependencies import TelegramIDDep
from api.v1.wallet.dependencies import WalletServiceDep
from api.v1.wallet.schemas import WalletResponse, WalletCurrencyList

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("/currencies", response_model=WalletCurrencyList)
async def get_currencies(wallet_service: WalletServiceDep) -> WalletCurrencyList:
    return wallet_service.get_currencies()


@router.get("", response_model=list[WalletResponse])
async def get_all_wallets(
    telegram_id: TelegramIDDep,
    wallet_service: WalletServiceDep
) -> list[WalletResponse]:
    return await wallet_service.get_wallets(telegram_id)


@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet(wallet_id: UUID, wallet_service: WalletServiceDep) -> WalletResponse:
    return await wallet_service.get_wallet(wallet_id)
