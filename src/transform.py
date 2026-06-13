def filter_currencies(rates: list[dict], currencies: list[str] = None) -> list[dict]:
    """Оставить только нужные валюты"""
    if currencies is None:
        currencies = ["USD", "EUR", "CNY", "GBP"]

    return [r for r in rates if r["char_code"] in currencies]


def calculate_cross_rate(
    rates: list[dict], from_code: str, to_code: str
) -> float | None:
    """Посчитать кросс-курс между двумя валютами"""
    rate_map = {r["char_code"]: r["rate"] / r["nominal"] for r in rates}

    if from_code not in rate_map or to_code not in rate_map:
        return None

    return round(rate_map[from_code] / rate_map[to_code], 6)
