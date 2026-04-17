# tests/test_health.py
from backend.excel_reader import BaseConfig
from backend.health import calcular_status

def make_config(**kwargs):
    defaults = dict(
        nome_base="b", schema_tabela="s.b", filtro_sql="",
        coluna_data="dt", data_evolui=True, coluna_saldo="vl",
        coluna_cobertura="cpf", tipo_cobertura="cpf", checar_linhas=True,
    )
    defaults.update(kwargs)
    return BaseConfig(**defaults)

def test_primeiro_check_quando_sem_anterior():
    config = make_config()
    atual = {"total_linhas": 1000, "max_data": "2026-04-15", "soma_saldo": 5000.0}
    resultado = calcular_status(config, atual, None)
    assert resultado["status"] == "PRIMEIRO_CHECK"
    assert resultado["erro_linhas"] is False
    assert resultado["erro_saldo"] is False
    assert resultado["erro_data"] is False

def test_ok_quando_dentro_dos_limites():
    config = make_config()
    atual = {"total_linhas": 1050, "max_data": "2026-04-15", "soma_saldo": 5100.0}
    anterior = {"total_linhas": 1000, "max_data": "2026-04-14", "soma_saldo": 5000.0}
    resultado = calcular_status(config, atual, anterior)
    assert resultado["status"] == "OK"
    assert resultado["erro_linhas"] is False

def test_erro_linhas_abaixo_de_80_pct():
    config = make_config(checar_linhas=True)
    atual = {"total_linhas": 700, "max_data": "2026-04-15", "soma_saldo": 5000.0}
    anterior = {"total_linhas": 1000, "max_data": "2026-04-14", "soma_saldo": 5000.0}
    resultado = calcular_status(config, atual, anterior)
    assert resultado["erro_linhas"] is True
    assert resultado["status"] == "ERRO"

def test_erro_linhas_acima_de_120_pct():
    config = make_config(checar_linhas=True)
    atual = {"total_linhas": 1300, "max_data": "2026-04-15", "soma_saldo": 5000.0}
    anterior = {"total_linhas": 1000, "max_data": "2026-04-14", "soma_saldo": 5000.0}
    resultado = calcular_status(config, atual, anterior)
    assert resultado["erro_linhas"] is True

def test_nao_verifica_linhas_quando_checar_linhas_false():
    config = make_config(checar_linhas=False)
    atual = {"total_linhas": 100, "max_data": "2026-04-15", "soma_saldo": 5000.0}
    anterior = {"total_linhas": 1000, "max_data": "2026-04-14", "soma_saldo": 5000.0}
    resultado = calcular_status(config, atual, anterior)
    assert resultado["erro_linhas"] is False

def test_erro_saldo_quando_varia_mais_de_20_pct():
    config = make_config()
    atual = {"total_linhas": 1000, "max_data": "2026-04-15", "soma_saldo": 7000.0}
    anterior = {"total_linhas": 1000, "max_data": "2026-04-14", "soma_saldo": 5000.0}
    resultado = calcular_status(config, atual, anterior)
    assert resultado["erro_saldo"] is True

def test_nao_verifica_saldo_quando_sem_coluna():
    config = make_config(coluna_saldo="sem_coluna")
    atual = {"total_linhas": 1000, "max_data": "2026-04-15", "soma_saldo": None}
    anterior = {"total_linhas": 1000, "max_data": "2026-04-14", "soma_saldo": None}
    resultado = calcular_status(config, atual, anterior)
    assert resultado["erro_saldo"] is False

def test_erro_data_quando_data_nao_evoluiu():
    config = make_config(data_evolui=True)
    atual = {"total_linhas": 1000, "max_data": "2026-04-14", "soma_saldo": 5000.0}
    anterior = {"total_linhas": 1000, "max_data": "2026-04-14", "soma_saldo": 5000.0}
    resultado = calcular_status(config, atual, anterior)
    assert resultado["erro_data"] is True

def test_sem_erro_data_quando_data_igual_e_nao_evolui():
    config = make_config(data_evolui=False)
    atual = {"total_linhas": 1000, "max_data": "2026-04-14", "soma_saldo": 5000.0}
    anterior = {"total_linhas": 1000, "max_data": "2026-04-14", "soma_saldo": 5000.0}
    resultado = calcular_status(config, atual, anterior)
    assert resultado["erro_data"] is False

def test_erro_data_quando_data_diminuiu_e_nao_evolui():
    config = make_config(data_evolui=False)
    atual = {"total_linhas": 1000, "max_data": "2026-04-13", "soma_saldo": 5000.0}
    anterior = {"total_linhas": 1000, "max_data": "2026-04-14", "soma_saldo": 5000.0}
    resultado = calcular_status(config, atual, anterior)
    assert resultado["erro_data"] is True
