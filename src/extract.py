import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# ЦБ РФ отдаёт данные в формате XML
CBR_URL = "https://www.cbr.ru/scripts/XML_daily.asp"


def fetch_rates(on_date: datetime = None) -> str:
    """Скачать XML с курсами валют с сайта ЦБ РФ"""
    params = {}
    if on_date:
        params["date_req"] = on_date.strftime("%d/%m/%Y")
    response = requests.get(CBR_URL, params=params, timeout=10)
    response.raise_for_status()  # упадёт если статус не 200
    response.encoding = "windows-1251"  # ЦБ РФ отдаёт в этой кодировке
    return response.text


def parse_rates(xml_text: str) -> list[dict]:
    """Распарсить XML и вернуть список словарей"""
    root = ET.fromstring(xml_text)

    now = datetime.now().replace(second=0, microsecond=0)

    rates = []
    for valute in root.findall("Valute"):
        rates.append(
            {
                "char_code": valute.find("CharCode").text,
                "name": valute.find("Name").text,
                "nominal": int(valute.find("Nominal").text),
                "rate": float(valute.find("Value").text.replace(",", ".")),
                "date": now,
            }
        )

    return rates
