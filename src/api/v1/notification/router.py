from fastapi import APIRouter, status

from api.v1.notification.schemas import NotificationResponse, MarkAsReadRequest
from api.v1.notification.dependencies import NotificationServiceDep
from api.v1.auth.dependencies import UserAuthDep
from api.v1.base.dependencies import PaginationDep

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=NotificationResponse,
    summary="Получить уведомления",
    description="Возвращает список уведомлений пользователя с поддержкой пагинации.\n\n"
               "**Типы уведомлений:**\n"
               "- `operation_status` - изменение статуса операции\n"
               "- `referral_deposit` - начисление на реферальный баланс\n"
               "- `referral_join` - присоединение через реферальную ссылку\n\n"
               "**Параметры пагинации:**\n"
               "- `limit` - количество уведомлений на страницу (по умолчанию: все)\n"
               "- `offset` - смещение от начала списка (по умолчанию: 0)\n\n"
               "**Требования:**\n"
               "- Пользователь должен быть авторизован\n",
    responses={
        200: {
            "description": "Уведомления успешно получены",
            "content": {
                "application/json": {
                    "example": {
                        "notifications": [
                            {
                                "notification_id": "550e8400-e29b-41d4-a716-446655440000",
                                "type": "referral_deposit",
                                "title": "Начисление на реферальный баланс",
                                "message": "Начислено 100.50 USDt от реферала @username123",
                                "created_at": "2024-01-15T10:30:00",
                                "read": False,
                                "image_url": None,
                                "detail_image_url": None,
                                "action_url": "https://example.com/promo",
                                "action_label": "Ознакомиться"
                            }
                        ],
                        "total": 1,
                        "unread_count": 1,
                        "limit": 10,
                        "offset": 0
                    }
                }
            }
        }
    }
)
async def get_notifications(
    user: UserAuthDep,
    service: NotificationServiceDep,
    pagination: PaginationDep
):
    """
    Получить уведомления пользователя с пагинацией.
    
    Возвращает список всех уведомлений пользователя,
    включая количество непрочитанных.
    """
    return await service.get_notifications(
        user.id,
        limit=pagination.limit,
        offset=pagination.offset
    )


@router.post(
    "/read",
    status_code=status.HTTP_200_OK,
    summary="Отметить уведомления как прочитанные",
    description="Отмечает указанные уведомления как прочитанные.\n\n"
               "**Требования:**\n"
               "- Пользователь должен быть авторизован\n",
    responses={
        200: {
            "description": "Уведомления отмечены как прочитанные",
            "content": {
                "application/json": {
                    "example": {
                        "marked_count": 2
                    }
                }
            }
        }
    }
)
async def mark_notifications_as_read(
    user: UserAuthDep,
    service: NotificationServiceDep,
    request: MarkAsReadRequest
):
    """
    Отметить уведомления как прочитанные.
    
    Принимает список ID уведомлений и отмечает их как прочитанные.
    Возвращает количество отмеченных уведомлений.
    """
    marked_count = await service.mark_as_read(user.id, request.notification_ids)
    return {"marked_count": marked_count}

