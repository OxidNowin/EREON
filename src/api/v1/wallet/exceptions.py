class WalletNotFoundError(Exception):
    """Кошелек не найден"""
    
    def __init__(self, message: str = "Wallet not found"):
        self.message = message
        super().__init__(self.message)


class NetworkNotFoundError(Exception):
    """Ошибка: сеть для адреса не найдена"""
    
    def __init__(self, message: str = "Network not found for address"):
        self.message = message
        super().__init__(self.message)


class InsufficientFundsError(Exception):
    """Недостаточно средств"""
    
    def __init__(self, message: str = "Insufficient funds"):
        self.message = message
        super().__init__(self.message)
