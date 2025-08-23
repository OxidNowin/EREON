from fastapi import APIRouter, status

from api.v1.user.schemas import UserChangeCode
from api.v1.user.dependencies import UserServiceDep
from api.v1.auth.dependencies import UserAuthDep

router = APIRouter(prefix="/user", tags=["User"])


@router.patch(
    "/entry_code", 
    status_code=status.HTTP_200_OK,
    summary="Изменить код входа",
    description="Позволяет пользователю изменить свой 4-значный код входа.\n\n"
               "**Процесс изменения кода:**\n"
               "1. Пользователь указывает текущий (старый) код входа\n"
               "2. Пользователь указывает новый желаемый код входа\n"
               "3. Система проверяет корректность старого кода\n"
               "4. При успешной проверке код заменяется на новый\n\n"
               "**Требования:**\n"
               "- Пользователь должен быть авторизован\n"
               "- Старый код должен быть корректным\n"
               "- Новый код должен соответствовать требованиям (4 цифры)\n\n"
               "**Безопасность:**\n"
               "- Изменение кода требует знания текущего кода\n"
               "- Новый код должен отличаться от старого\n"
               "- Код должен содержать ровно 4 символа",
    responses={
        200: {
            "description": "Код входа успешно изменен",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Код входа успешно обновлен"
                    }
                }
            }
        },
        400: {
            "description": "Ошибка обновления кода входа",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Failed to update entry code. Old code may be incorrect.",
                        "type": "EntryCodeUpdateError"
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
                                "loc": ["body", "new_code"],
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
async def change_entry_code(
    user: UserAuthDep,
    codes: UserChangeCode, 
    service: UserServiceDep
):
    """
    Изменить код входа.
    
    Позволяет авторизованному пользователю изменить свой 4-значный код входа,
    указав текущий код и новый желаемый код.
    """
    await service.change_entry_code(user.id, codes)
