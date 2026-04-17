# tests/test_excel_reader.py
import pytest
import pandas as pd
from pathlib import Path
from backend.excel_reader import BaseConfig, ler_configuracoes

@pytest.fixture
def excel_path(tmp_path):
    df = pd.DataFrame([{
        "nome_base": "base_credito",
        "schema_tabela": "dw.base_credito",
        "filtro_sql": "WHERE ano_mes = '202412'",
        "coluna_data": "dt_referencia",
        "data_evolui": "sim",
        "coluna_saldo": "vl_saldo",
        "coluna_cobertura": "cpf_cnpj",
        "tipo_cobertura": "cpf",
        "checar_linhas": "sim",
    }, {
        "nome_base": "base_sem_data",
        "schema_tabela": "dw.base_sem_data",
        "filtro_sql": "",
        "coluna_data": "sem_coluna",
        "data_evolui": "nao",
        "coluna_saldo": "sem_coluna",
        "coluna_cobertura": "sem_coluna",
        "tipo_cobertura": "cpf",
        "checar_linhas": "nao",
    }])
    path = tmp_path / "bases_config.xlsx"
    df.to_excel(path, index=False)
    return path

def test_ler_configuracoes_retorna_lista(excel_path):
    configs = ler_configuracoes(excel_path)
    assert len(configs) == 2

def test_campos_bool_convertidos(excel_path):
    configs = ler_configuracoes(excel_path)
    assert configs[0].data_evolui is True
    assert configs[0].checar_linhas is True
    assert configs[1].data_evolui is False
    assert configs[1].checar_linhas is False

def test_campos_string_preservados(excel_path):
    configs = ler_configuracoes(excel_path)
    assert configs[0].nome_base == "base_credito"
    assert configs[0].filtro_sql == "WHERE ano_mes = '202412'"
    assert configs[1].filtro_sql == ""
    assert configs[1].coluna_data == "sem_coluna"
