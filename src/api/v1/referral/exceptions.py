class ReferralNotFoundError(Exception):
    """Реферал не найден"""
    
    def __init__(self, message: str = "Referral not found"):
        self.message = message
        super().__init__(self.message)


class ReferralTypeAlreadySetError(Exception):
    """Тип реферальной программы уже установлен"""
    
    def __init__(self, message: str = "Referral type already set"):
        self.message = message
        super().__init__(self.message)


class ReferralUpdateError(Exception):
    """Ошибка обновления реферальной программы"""
    
    def __init__(self, message: str = "Failed to update referral"):
        self.message = message
        super().__init__(self.message)
