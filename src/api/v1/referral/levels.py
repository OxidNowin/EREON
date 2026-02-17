from decimal import Decimal


LEVEL_THRESHOLDS = [0, 3, 5, 8, 10]


def get_revenue_share_level(referral_count: int) -> int:
    """
    Возвращает уровень реферальной программы (1–5) по количеству рефералов.
    """
    if referral_count >= 10:
        return 5
    if referral_count >= 8:
        return 4
    if referral_count >= 5:
        return 3
    if referral_count >= 3:
        return 2
    return 1


def get_revenue_share_percentage(referral_count: int) -> Decimal:
    """
    Возвращает процент реферальной программы по количеству рефералов.
    """
    if referral_count >= 10:
        return Decimal("0.50")
    if referral_count >= 8:
        return Decimal("0.40")
    if referral_count >= 5:
        return Decimal("0.30")
    if referral_count >= 3:
        return Decimal("0.20")
    return Decimal("0.00")


def get_next_level_referrals_needed(referral_count: int) -> int | None:
    """
    Возвращает, сколько рефералов не хватает до следующего уровня.
    Если текущий уровень максимальный, возвращает None.
    """
    for threshold in LEVEL_THRESHOLDS:
        if threshold > referral_count:
            return threshold - referral_count
    return None


