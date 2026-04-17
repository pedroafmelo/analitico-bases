# tests/test_collector.py
import datetime
from unittest.mock import MagicMock, patch
from backend.collector import coletar_base, _inferir_tipo, _executar_query

def test_inferir_tipo_numerico():
    import decimal
    assert _inferir_tipo(float) == "numérico"
    assert _inferir_tipo(int) == "numérico"
    assert _inferir_tipo(decimal.Decimal) == "numérico"

def test_inferir_tipo_data():
    assert _inferir_tipo(datetime.date) == "data"
    assert _inferir_tipo(datetime.datetime) == "data"

def test_inferir_tipo_texto():
    assert _inferir_tipo(str) == "texto"
    assert _inferir_tipo(bytes) == "texto"

def test_executar_query_retorna_ok_com_duracao():
    cursor = MagicMock()
    cursor.fetchone.return_value = (1000,)
    cursor.description = [("total_linhas", int, None, None, None, None, None)]
    status, duracao, row = _executar_query(cursor, "SELECT COUNT(*) as total_linhas FROM t")
    assert status == "OK"
    assert duracao > 0
    assert row == {"total_linhas": 1000}

def test_executar_query_captura_timeout():
    import pyodbc
    cursor = MagicMock()
    cursor.execute.side_effect = pyodbc.OperationalError("timeout")
    status, duracao, row = _executar_query(cursor, "SELECT 1")
    assert status == "TIMEOUT"
    assert row is None
