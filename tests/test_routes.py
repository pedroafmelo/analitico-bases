# tests/test_routes.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.main import app
from backend.database import criar_tabelas, salvar_checagem
import sqlite3

@pytest.fixture
def client(monkeypatch):
    # Use a thread-safe in-memory db (check_same_thread=False for FastAPI's thread pool)
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    criar_tabelas(conn)

    # Patch get_connection to return in-memory db
    monkeypatch.setattr("backend.routes.bases.get_connection", lambda: conn)
    monkeypatch.setattr("backend.routes.checagens.get_connection", lambda: conn)
    monkeypatch.setattr("backend.routes.sondar.get_connection", lambda: conn)
    # Seed one checagem
    salvar_checagem(conn, {
        "nome_base": "base_a", "dt_checagem": "2026-04-16T08:00:00",
        "total_linhas": 1000, "max_data": "2026-04-15", "soma_saldo": 5000.0,
        "total_cobertura_base": 800, "total_cobertura_sicredi": 1200,
        "pct_sicredi": 0.52, "pct_fisital": 0.38, "pct_woop": 0.10,
        "duracao_query_segundos": 3.2, "status_consulta": "OK",
        "erro_linhas": 0, "erro_saldo": 0, "erro_data": 0, "status": "OK",
    }, [
        {"nome_coluna": "cpf_cnpj", "tipo_dado": "texto", "total_nulos": 0, "pct_nulos": 0.0, "soma_valor": None},
    ])
    yield TestClient(app)
    conn.close()

def test_get_bases_retorna_lista(client):
    r = client.get("/api/bases")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["nome_base"] == "base_a"

def test_get_base_por_nome(client):
    r = client.get("/api/bases/base_a")
    assert r.status_code == 200
    assert r.json()["total_linhas"] == 1000

def test_get_base_nao_encontrada_retorna_404(client):
    r = client.get("/api/bases/inexistente")
    assert r.status_code == 404

def test_get_historico(client):
    r = client.get("/api/bases/base_a/historico")
    assert r.status_code == 200
    assert len(r.json()) == 1
