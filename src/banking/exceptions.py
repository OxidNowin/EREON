class BankApiError(Exception):
    """Общая ошибка при работе с банковским API"""
    
    def __init__(self, message: str, status_code: int | None = None, response_data: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class BankTokenError(Exception):
    """Ошибка получения токена доступа от банковского API"""
    
    def __init__(self, message: str, status_code: int | None = None, response_data: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message) 