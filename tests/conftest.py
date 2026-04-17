import sys
import types
import sqlite3
import pytest

# ---------------------------------------------------------------------------
# Provide a lightweight pyodbc stub so tests can run on machines where the
# real pyodbc C extension cannot be loaded (e.g. macOS without unixODBC).
# ---------------------------------------------------------------------------
if "pyodbc" not in sys.modules:
    _pyodbc_stub = types.ModuleType("pyodbc")

    class _OperationalError(Exception):
        pass

    class _Error(Exception):
        pass

    _pyodbc_stub.OperationalError = _OperationalError
    _pyodbc_stub.Error = _Error
    _pyodbc_stub.connect = None  # tests that need real connections must mock this
    sys.modules["pyodbc"] = _pyodbc_stub


@pytest.fixture
def db_conn():
    from backend.database import criar_tabelas
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    criar_tabelas(conn)
    yield conn
    conn.close()


@pytest.fixture
def base_config_sample():
    from backend.excel_reader import BaseConfig
    return BaseConfig(
        nome_base="base_teste",
        schema_tabela="dw.base_teste",
        filtro_sql="",
        coluna_data="dt_ref",
        data_evolui=True,
        coluna_saldo="vl_saldo",
        coluna_cobertura="cpf_cnpj",
        tipo_cobertura="cpf",
        checar_linhas=True,
    )
