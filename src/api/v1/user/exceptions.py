class EntryCodeUpdateError(Exception):
    """Ошибка обновления кода входа"""
    
    def __init__(self, message: str = "Failed to update entry code"):
        self.message = message
        super().__init__(self.message)
