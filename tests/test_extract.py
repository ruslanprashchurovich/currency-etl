import responses
import requests
import pytest
from src.extract import fetch_rates, parse_rates

MOCK_XML = """<?xml version="1.0" encoding="windows-1251"?>
<ValCurs Date="06.06.2026" name="Foreign Currency Market">
    <Valute ID="R01235">
        <CharCode>USD</CharCode>
        <Nominal>1</Nominal>
        <Name>Доллар США</Name>
        <Value>92,5034</Value>
    </Valute>
    <Valute ID="R01239">
        <CharCode>EUR</CharCode>
        <Nominal>1</Nominal>
        <Name>Евро</Name>
        <Value>99,1234</Value>
    </Valute>
</ValCurs>"""


@responses.activate
def test_fetch_rates():
    """Проверить что запрос уходит на правильный URL"""
    responses.add(
        responses.GET,
        "https://www.cbr.ru/scripts/XML_daily.asp",
        body=MOCK_XML.encode("windows-1251"),
        status=200,
    )
    result = fetch_rates()
    assert "USD" in result
    assert "EUR" in result


@responses.activate
def test_fetch_rates_error():
    """Проверить что ошибка сервера пробрасывается"""
    responses.add(
        responses.GET,
        "https://www.cbr.ru/scripts/XML_daily.asp",
        status=500,
    )
    with pytest.raises(requests.HTTPError):
        fetch_rates()


def test_parse_rates():
    """Проверить парсинг XML"""
    rates = parse_rates(MOCK_XML)
    assert len(rates) == 2

    usd = next(r for r in rates if r["char_code"] == "USD")
    assert usd["rate"] == 92.5034
    assert usd["nominal"] == 1
    assert usd["name"] == "Доллар США"
