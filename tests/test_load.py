import os
from unittest.mock import patch, MagicMock
from src.load import get_connection, init_db, save_rates


@patch.dict(
    os.environ,
    {
        "DB_HOST": "db",
        "DB_PORT": "5432",
        "DB_NAME": "currency_db",
        "DB_USER": "admin",
        "DB_PASSWORD": "secret",
    },
)
@patch("src.load.psycopg2.connect")
def test_get_connection(mock_connect):
    get_connection()
    mock_connect.assert_called_once_with(
        host="db",
        port="5432",
        dbname="currency_db",
        user="admin",
        password="secret",
    )


@patch("src.load.get_connection")
def test_init_db_creates_table(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn

    init_db()

    assert mock_conn.cursor.called
    calls = mock_cursor.execute.call_args_list
    assert any("CREATE TABLE IF NOT EXISTS currency_rates" in c[0][0] for c in calls)
    assert any("CREATE INDEX IF NOT EXISTS idx_currency_date" in c[0][0] for c in calls)
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("src.load.get_connection")
def test_save_rates_inserts_data(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 2
    mock_conn.cursor.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn

    rates = [
        {
            "char_code": "USD",
            "name": "Доллар США",
            "nominal": 1,
            "rate": 92.50,
            "date": "2026-06-13",
        },
        {
            "char_code": "EUR",
            "name": "Евро",
            "nominal": 1,
            "rate": 99.12,
            "date": "2026-06-13",
        },
    ]

    save_rates(rates)

    mock_cursor.executemany.assert_called_once()
    sql, params = mock_cursor.executemany.call_args[0]
    assert "INSERT INTO currency_rates" in sql
    assert params == rates
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("src.load.get_connection")
def test_save_rates_empty_list(mock_get_conn):
    save_rates([])
    mock_get_conn.assert_not_called()
