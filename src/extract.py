import requests
import xml.etree.ElementTree as ET
from datetime import date

# ЦБ РФ отдаёт данные в формате XML
CBR_URL = "https://www.cbr.ru/scripts/XML_daily.asp"


def fetch_rates(on_date: date = None) -> str:
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

    # Дата из атрибута корневого элемента
    raw_date = root.attrib.get("Date", "")
    rate_date = date.today()
    if raw_date:
        from datetime import datetime

        rate_date = datetime.strptime(raw_date, "%d.%m.%Y").date()

    rates = []
    for valute in root.findall("Valute"):
        rates.append(
            {
                "char_code": valute.find("CharCode").text,  # USD, EUR...
                "name": valute.find("Name").text,  # Доллар США
                "nominal": int(valute.find("Nominal").text),  # 1, 10, 100...
                "rate": float(valute.find("Value").text.replace(",", ".")),  # 92.5034
                "date": rate_date,
            }
        )

    return rates
