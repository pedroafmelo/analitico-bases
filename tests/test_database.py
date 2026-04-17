# tests/test_database.py
import sqlite3
from backend.database import criar_tabelas, salvar_checagem, buscar_ultima_checagem, listar_bases

def test_criar_tabelas_cria_schema(db_conn):
    cursor = db_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    assert "checagens" in tables
    assert "metricas_colunas" in tables

def test_salvar_e_buscar_checagem(db_conn):
    checagem = {
        "nome_base": "base_a",
        "dt_checagem": "2026-04-16T08:00:00",
        "total_linhas": 1000,
        "max_data": "2026-04-15",
        "soma_saldo": 5000.0,
        "total_cobertura_base": 800,
        "total_cobertura_sicredi": 1200,
        "pct_sicredi": 0.52,
        "pct_fisital": 0.38,
        "pct_woop": 0.10,
        "duracao_query_segundos": 3.2,
        "status_consulta": "OK",
        "erro_linhas": 0,
        "erro_saldo": 0,
        "erro_data": 0,
        "status": "PRIMEIRO_CHECK",
    }
    metricas = [
        {"nome_coluna": "cpf_cnpj", "tipo_dado": "texto", "total_nulos": 0, "pct_nulos": 0.0, "soma_valor": None},
        {"nome_coluna": "vl_saldo", "tipo_dado": "numérico", "total_nulos": 0, "pct_nulos": 0.0, "soma_valor": 5000.0},
    ]
    checagem_id = salvar_checagem(db_conn, checagem, metricas)
    assert checagem_id == 1

    ultima = buscar_ultima_checagem(db_conn, "base_a")
    assert ultima["total_linhas"] == 1000
    assert ultima["status"] == "PRIMEIRO_CHECK"

def test_buscar_ultima_checagem_retorna_none_se_nao_existe(db_conn):
    assert buscar_ultima_checagem(db_conn, "inexistente") is None

def test_listar_bases_retorna_ultima_por_base(db_conn):
    for dt, linhas in [("2026-04-15T08:00:00", 900), ("2026-04-16T08:00:00", 1000)]:
        salvar_checagem(db_conn, {
            "nome_base": "base_a", "dt_checagem": dt, "total_linhas": linhas,
            "max_data": None, "soma_saldo": None, "total_cobertura_base": None,
            "total_cobertura_sicredi": None, "pct_sicredi": None, "pct_fisital": None,
            "pct_woop": None, "duracao_query_segundos": 2.0, "status_consulta": "OK",
            "erro_linhas": 0, "erro_saldo": 0, "erro_data": 0, "status": "OK",
        }, [])
    bases = listar_bases(db_conn)
    assert len(bases) == 1
    assert bases[0]["total_linhas"] == 1000
