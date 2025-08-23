from fastapi import APIRouter, status

from api.v1.auth.schemas import UserLogin
from api.v1.auth.dependencies import LoginServiceDep

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Войти в систему по коду",
    description="Аутентификация пользователя по коду входа\n"
                "*Необходимо при наличии установленного кода*\n\n"
                "Доступ выдается на 15 минут и автоматически обновляется при вызове других эндпоинтов"
               "**Процесс аутентификации:**\n"
               "1. Пользователь вводит свой Telegram ID и 4-значный код входа\n"
               "2. Система проверяет корректность кода\n"
               "3. При успешной аутентификации пользователь получает доступ к API\n\n"
               "**Требования:**\n"
               "- Пользователь должен быть зарегистрирован в системе\n"
               "- Код входа должен быть корректным\n"
               "- Telegram ID должен соответствовать зарегистрированному пользователю\n\n",
    responses={
        204: {
            "description": "Пользователь успешно вошел в систему",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Успешная аутентификация"
                    }
                }
            }
        },
        401: {
            "description": "Неверный код входа",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Invalid entry code for user with telegram_id 123456789",
                        "type": "InvalidEntryCodeError"
                    }
                }
            }
        },
        422: {
            "description": "Ошибка валидации данных",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Validation error",
                        "type": "RequestValidationError",
                        "details": [
                            {
                                "loc": ["body", "entry_code"],
                                "msg": "ensure this value has at least 4 characters",
                                "type": "value_error.any_str.min_length"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def login_user(data: UserLogin, service: LoginServiceDep):
    """
    Войти в систему по коду.
    
    Аутентифицирует пользователя по Telegram ID и 4-значному коду входа.
    После успешной аутентификации пользователь получает доступ к защищенным эндпоинтам API.
    """
    await service.login_by_code(data)
