import re
from typing import Iterator, Callable
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class NetworkConfig:
    """Конфигурация сети с валидатором и комиссией"""
    name: str
    validator: Callable[[str], bool]
    fee: Decimal

    def __post_init__(self):
        if self.fee < 0:
            raise ValueError(f"Комиссия не может быть отрицательной для сети {self.name}")


class WalletAddressMatcher:
    _validators: dict[str, Callable[[str], bool]] = {}

    def __init__(self):
        self._networks: list[NetworkConfig] = [
            NetworkConfig(
                name="TRC20",
                validator=self._validators.get("TRC20", lambda x: False),
                fee=Decimal("2.75")
            ),
        ]

    @classmethod
    def validator(cls, network_name: str):
        """Декоратор для регистрации валидатора сети"""
        def decorator(func: Callable[[str], bool]):
            cls._validators[network_name] = func
            return func
        return decorator

    def iter_matched(self, addresses: list[str]) -> Iterator[tuple[str, str]]:
        """Итератор по всем совпавшим адресам с их сетями"""
        for address in addresses:
            if (network := self.match(address)) is not None:
                yield network, address

    def match(self, address: str) -> str | None:
        """Определяет сеть для данного адреса"""
        for config in self._networks:
            if config.validator(address):
                return config.name
        return None

    def get_network_fee(self, address: str) -> Decimal | None:
        """Определяет сеть для адреса и возвращает комиссию в Decimal"""
        for config in self._networks:
            if config.validator(address):
                return config.fee
        return None


@WalletAddressMatcher.validator("TRC20")
def validate_trc20(address: str) -> bool:
    """Валидация адреса TRC20 (TRON)"""
    return bool(re.fullmatch(r"T[1-9A-HJ-NP-Za-km-z]{33}", address))


matcher = WalletAddressMatcher()
