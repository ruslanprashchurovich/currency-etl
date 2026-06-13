import schedule
import time
from extract import fetch_rates, parse_rates
from transform import filter_currencies
from load import init_db, save_rates
from datetime import datetime


def run_pipeline():
    """Один запуск ETL пайплайна"""
    print(f"\n{'='*40}")
    print(f"🚀 Запуск пайплайна: {datetime.now():%Y-%m-%d %H:%M:%S}")

    try:
        # Extract — загрузить данные
        print("📥 Загружаем данные с ЦБ РФ...")
        xml_text = fetch_rates()
        all_rates = parse_rates(xml_text)
        print(f"   Получено валют: {len(all_rates)}")

        # Transform — обработать данные
        print("⚙️  Фильтруем валюты...")
        rates = filter_currencies(all_rates, ["USD", "EUR", "CNY", "GBP", "JPY"])
        print(f"   Оставлено валют: {len(rates)}")
        for r in rates:
            print(f"   {r['char_code']}: {r['rate']} руб.")

        # Load — сохранить в БД
        print("💾 Сохраняем в PostgreSQL...")
        save_rates(rates)

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    # Инициализировать БД при старте
    init_db()

    # Запустить сразу при старте
    run_pipeline()

    # Потом каждую минуту
    schedule.every(1).minutes.do(run_pipeline)

    print("\n⏰ Планировщик запущен — обновление каждую минуту")
    while True:
        schedule.run_pending()
        time.sleep(5)
