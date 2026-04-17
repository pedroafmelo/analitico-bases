from backend.excel_reader import BaseConfig

def build_aggregate_query(config: BaseConfig, columns: list[dict]) -> str:
    parts = ["COUNT(*) as total_linhas"]

    if config.coluna_data != "sem_coluna":
        parts.append(f"MAX({config.coluna_data}) as max_data")

    if config.coluna_saldo != "sem_coluna":
        parts.append(f"SUM({config.coluna_saldo}) as soma_saldo")

    if config.coluna_cobertura != "sem_coluna":
        parts.append(f"COUNT(DISTINCT {config.coluna_cobertura}) as total_cobertura_base")

    for col in columns:
        nome = col["nome"]
        parts.append(f"COUNT(CASE WHEN {nome} IS NULL THEN 1 END) as nulls_{nome}")
        if col["tipo"] == "numérico":
            parts.append(f"SUM({nome}) as sum_{nome}")

    query = f"SELECT {', '.join(parts)} FROM {config.schema_tabela}"
    if config.filtro_sql:
        query += f" {config.filtro_sql}"

    return query

def build_coverage_query(config: BaseConfig) -> str | None:
    if config.coluna_cobertura == "sem_coluna":
        return None

    join_col = "cpf_cnpj" if config.tipo_cobertura == "cpf" else "conta_principal"

    query = f"""
SELECT
    COUNT(DISTINCT a.{join_col}) as total_cobertura_sicredi,
    SUM(CASE WHEN a.des_core = 'SICREDI' THEN 1.0 ELSE 0 END) / NULLIF(COUNT(*), 0) as pct_sicredi,
    SUM(CASE WHEN a.des_core = 'FISITAL' THEN 1.0 ELSE 0 END) / NULLIF(COUNT(*), 0) as pct_fisital,
    SUM(CASE WHEN a.des_core = 'WOOP'    THEN 1.0 ELSE 0 END) / NULLIF(COUNT(*), 0) as pct_woop
FROM {config.schema_tabela} b
JOIN associados_total_diario a ON a.{join_col} = b.{config.coluna_cobertura}
""".strip()

    if config.filtro_sql:
        query += f"\n{config.filtro_sql}"

    return query
