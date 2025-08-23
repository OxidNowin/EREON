class PaymentProcessingError(Exception):
    """Ошибка обработки платежа"""
    
    def __init__(self, message: str = "Payment processing failed"):
        self.message = message
        super().__init__(self.message)


class PaymentLinkError(Exception):
    """Ошибка получения данных платежной ссылки"""
    
    def __init__(self, message: str = "Failed to get payment link data"):
        self.message = message
        super().__init__(self.message)
