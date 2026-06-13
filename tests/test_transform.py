from src.transform import filter_currencies, calculate_cross_rate

RATES = [
    {"char_code": "USD", "rate": 92.50, "nominal": 1},
    {"char_code": "EUR", "rate": 99.12, "nominal": 1},
    {"char_code": "CNY", "rate": 12.75, "nominal": 1},
    {"char_code": "GBP", "rate": 116.30, "nominal": 1},
]


def test_filter_currencies():
    result = filter_currencies(RATES, ["USD", "EUR"])
    assert len(result) == 2
    assert all(r["char_code"] in ["USD", "EUR"] for r in result)


def test_filter_unknown_currency():
    result = filter_currencies(RATES, ["XYZ"])
    assert result == []


def test_cross_rate():
    rate = calculate_cross_rate(RATES, "EUR", "USD")
    assert rate == round(99.12 / 92.50, 6)


def test_cross_rate_unknown():
    rate = calculate_cross_rate(RATES, "USD", "XYZ")
    assert rate is None
