import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Подключиться к PostgreSQL"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def init_db():
    """Создать таблицу если не существует"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS currency_rates (
            id          SERIAL PRIMARY KEY,
            char_code   VARCHAR(10) NOT NULL,
            name        VARCHAR(100),
            nominal     INTEGER,
            rate        NUMERIC(12, 4),
            date        DATE NOT NULL,
            loaded_at   TIMESTAMP DEFAULT NOW(),

            -- Уникальность: одна запись на валюту в день
            UNIQUE (char_code, date)
        );

        CREATE INDEX IF NOT EXISTS idx_currency_date
            ON currency_rates (char_code, date);
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ БД инициализирована")


def save_rates(rates: list[dict]):
    """Сохранить курсы в БД"""
    if not rates:
        print("⚠️ Нет данных для сохранения")
        return

    conn = get_connection()
    cursor = conn.cursor()

    # INSERT ... ON CONFLICT — если запись уже есть (та же валюта + дата)
    # обновить курс вместо ошибки
    cursor.executemany(
        """
        INSERT INTO currency_rates (char_code, name, nominal, rate, date)
        VALUES (%(char_code)s, %(name)s, %(nominal)s, %(rate)s, %(date)s)
        ON CONFLICT (char_code, date)
        DO UPDATE SET
            rate      = EXCLUDED.rate,
            loaded_at = NOW();
    """,
        rates,
    )

    conn.commit()
    print(f"✅ Сохранено {cursor.rowcount} записей")
    cursor.close()
    conn.close()
