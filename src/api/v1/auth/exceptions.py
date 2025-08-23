class InvalidEntryCodeError(Exception):
    """Неверный код входа"""
    
    def __init__(self, message: str = "Invalid entry code"):
        self.message = message
        super().__init__(self.message)
