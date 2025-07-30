class AlfaTokenError(Exception):
    """Ошибка получения токена доступа от Alfa Bank API"""
    
    def __init__(self, message: str, status_code: int | None = None, response_data: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class AlfaApiError(Exception):
    """Общая ошибка при работе с Alfa Bank API"""
    
    def __init__(self, message: str, status_code: int | None = None, response_data: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)

class AlfaRsaSignatureError(Exception):
    """Ошибка подписи дайджеста ЭП"""
    def __init__(self):
        super().__init__("Ошибка подписи дайджеста")
