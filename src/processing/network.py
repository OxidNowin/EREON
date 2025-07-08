import re
from typing import Callable, Iterator


class WalletAddressMatcher:
    _validators: dict[str, Callable[[str], bool]] = {
        "TRC20": lambda address: bool(re.fullmatch(r"T[1-9A-HJ-NP-Za-km-z]{33}", address))
    }

    def iter_matched(self, addresses: list[str]) -> Iterator[tuple[str, str]]:
        for address in addresses:
            if (network := self.match(address)) is not None:
                yield network, address

    def match(self, address:str) -> str | None:
        result_network = None
        for network, validator in self._validators.items():
            if validator(address):
                result_network = network
                break

        return result_network
