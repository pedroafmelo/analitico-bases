# tests/test_query_builder.py
from backend.query_builder import build_aggregate_query, build_coverage_query
from backend.excel_reader import BaseConfig

def make_config(**kwargs):
    defaults = dict(
        nome_base="b", schema_tabela="dw.base_b", filtro_sql="",
        coluna_data="dt_ref", data_evolui=True, coluna_saldo="vl_saldo",
        coluna_cobertura="cpf_cnpj", tipo_cobertura="cpf", checar_linhas=True,
    )
    defaults.update(kwargs)
    return BaseConfig(**defaults)

COLS = [
    {"nome": "cpf_cnpj", "tipo": "texto"},
    {"nome": "vl_saldo", "tipo": "numérico"},
    {"nome": "dt_ref", "tipo": "data"},
]

def test_aggregate_inclui_count(base_config_sample):
    q = build_aggregate_query(base_config_sample, COLS)
    assert "COUNT(*) as total_linhas" in q

def test_aggregate_inclui_max_data_quando_configurada():
    config = make_config(coluna_data="dt_ref")
    q = build_aggregate_query(config, COLS)
    assert "MAX(dt_ref) as max_data" in q

def test_aggregate_omite_max_data_quando_sem_coluna():
    config = make_config(coluna_data="sem_coluna")
    q = build_aggregate_query(config, COLS)
    assert "max_data" not in q

def test_aggregate_inclui_sum_saldo():
    config = make_config(coluna_saldo="vl_saldo")
    q = build_aggregate_query(config, COLS)
    assert "SUM(vl_saldo) as soma_saldo" in q

def test_aggregate_inclui_nulls_por_coluna():
    config = make_config()
    q = build_aggregate_query(config, COLS)
    assert "CASE WHEN cpf_cnpj IS NULL" in q

def test_aggregate_inclui_sum_para_numericas():
    config = make_config()
    q = build_aggregate_query(config, COLS)
    assert "SUM(vl_saldo) as sum_vl_saldo" in q

def test_aggregate_nao_inclui_sum_para_texto():
    config = make_config()
    q = build_aggregate_query(config, COLS)
    assert "SUM(cpf_cnpj)" not in q

def test_aggregate_aplica_filtro():
    config = make_config(filtro_sql="WHERE ano_mes = '202412'")
    q = build_aggregate_query(config, COLS)
    assert "WHERE ano_mes = '202412'" in q

def test_coverage_retorna_none_quando_sem_coluna():
    config = make_config(coluna_cobertura="sem_coluna")
    assert build_coverage_query(config) is None

def test_coverage_usa_cpf_cnpj_para_tipo_cpf():
    config = make_config(tipo_cobertura="cpf")
    q = build_coverage_query(config)
    assert "a.cpf_cnpj" in q

def test_coverage_usa_conta_principal_para_tipo_conta():
    config = make_config(tipo_cobertura="conta")
    q = build_coverage_query(config)
    assert "a.conta_principal" in q
