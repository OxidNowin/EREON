import argparse
import asyncio
import random
import sys
from decimal import Decimal
from pathlib import Path
from uuid import UUID

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from infra.postgres.pg import get_db
from infra.postgres.uow import PostgresUnitOfWork
from infra.postgres.models import Operation, OperationStatus, OperationType, Wallet


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for creating mock operations."""
    parser = argparse.ArgumentParser(
        description="Create mock wallet operations for a specific wallet."
    )
    parser.add_argument(
        "--wallet-id",
        required=True,
        help="Wallet UUID for which operations will be created.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=30,
        help="Number of operations to create.",
    )
    parser.add_argument(
        "--min-amount",
        type=Decimal,
        default=Decimal("1.0"),
        help="Minimum operation amount.",
    )
    parser.add_argument(
        "--max-amount",
        type=Decimal,
        default=Decimal("10.0"),
        help="Maximum operation amount.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible results.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    """Validate parsed arguments."""
    if args.count <= 0:
        raise ValueError("Count must be greater than zero.")
    if args.min_amount <= Decimal("0"):
        raise ValueError("Minimum amount must be greater than zero.")
    if args.max_amount < args.min_amount:
        raise ValueError("Maximum amount must be greater than or equal to minimum amount.")


def generate_amount(min_amount: Decimal, max_amount: Decimal) -> Decimal:
    """Generate a random Decimal amount within the given range."""
    value = random.uniform(float(min_amount), float(max_amount))
    return Decimal(str(round(value, 6)))


async def create_mock_operations(
    wallet_id: UUID,
    count: int,
    min_amount: Decimal,
    max_amount: Decimal,
) -> None:
    """Create mock deposit and withdrawal operations for the given wallet."""
    async with get_db() as db:
        uow = PostgresUnitOfWork(db)

        wallet: Wallet | None = await uow.wallet.get_by_id(wallet_id)
        if wallet is None:
            raise ValueError(f"Wallet with id {wallet_id} not found.")

        for index in range(count):
            amount = generate_amount(min_amount, max_amount)

            if index % 2 == 0:
                fee = Decimal("0.0")
                operation = Operation(
                    wallet_id=wallet.wallet_id,
                    status=OperationStatus.CONFIRMED,
                    operation_type=OperationType.DEPOSIT,
                    amount=amount,
                    fee=fee,
                    total_amount=amount,
                )
                await uow.operation.add(operation)
                wallet.balance += amount
                continue

            fee = Decimal("0.0")
            total_amount = amount + fee

            if wallet.balance < total_amount:
                operation_status = OperationStatus.CANCELLED
            else:
                operation_status = OperationStatus.CONFIRMED

            operation = Operation(
                wallet_id=wallet.wallet_id,
                status=operation_status,
                operation_type=OperationType.WITHDRAW,
                amount=amount,
                fee=fee,
                total_amount=total_amount,
            )
            await uow.operation.add(operation)

            if operation_status is OperationStatus.CONFIRMED:
                wallet.balance -= total_amount


def main() -> None:
    """Entry point for creating mock operations via CLI."""
    args = parse_args()
    validate_args(args)

    if args.seed is not None:
        random.seed(args.seed)

    wallet_id = UUID(args.wallet_id)

    asyncio.run(
        create_mock_operations(
            wallet_id=wallet_id,
            count=args.count,
            min_amount=args.min_amount,
            max_amount=args.max_amount,
        )
    )


if __name__ == "__main__":
    main()

