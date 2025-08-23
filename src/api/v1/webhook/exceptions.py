class TransactionAlreadyExistsError(Exception):
    """Транзакция уже существует"""
    
    def __init__(self, message: str = "Transaction already exists"):
        self.message = message
        super().__init__(self.message)
