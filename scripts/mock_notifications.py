import argparse
import asyncio
import sys
from dataclasses import dataclass
from typing import Literal

from api.v1.base.service import BaseService
from infra.redis.redis_api import RedisAPI


@dataclass(slots=True)
class _DummyUnitOfWork:
    """
    Dummy unit of work for script usage.
    """


class MockNotificationService(BaseService):
    """
    Service for creating mock notifications via Redis.
    """

    async def create_mock_notification(
        self,
        telegram_id: int,
        title: str,
        message: str,
        notification_type: Literal["operation_status", "referral_deposit", "referral_join"] = "operation_status",
        max_notifications: int = 100,
    ) -> None:
        """
        Create a single mock notification for the given telegram_id.
        """
        await self._send_notification(
            telegram_id=telegram_id,
            notification_type=notification_type,
            title=title,
            message=message,
            max_notifications=max_notifications,
        )


async def _run(
    telegram_id: int,
    count: int,
) -> None:
    if telegram_id <= 0:
        raise ValueError("telegram_id must be a positive integer")
    if count <= 0:
        raise ValueError("count must be a positive integer")

    redis = RedisAPI()
    try:
        is_alive = await redis.ping()
        if not is_alive:
            raise RuntimeError("Redis is not available")

        service = MockNotificationService(uow=_DummyUnitOfWork(), redis=redis)

        for i in range(count):
            index = i + 1
            title = f"Тестовое уведомление #{index}"
            message = f"Мок-уведомление {index} для пользователя с telegram_id={telegram_id}"

            await service.create_mock_notification(
                telegram_id=telegram_id,
                title=title,
                message=message,
            )

        print(f"Создано {count} мок-уведомлений для telegram_id={telegram_id}")
    finally:
        await redis.close()


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Скрипт для создания мок-уведомлений в Redis по telegram_id.",
    )
    parser.add_argument(
        "--telegram-id",
        type=int,
        required=True,
        help="Telegram ID пользователя, для которого будут созданы уведомления.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=3,
        help="Количество мок-уведомлений, которые нужно создать (по умолчанию: 3).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        asyncio.run(_run(telegram_id=args.telegram_id, count=args.count))
    except Exception as exc:
        print(f"Ошибка при создании мок-уведомлений: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

