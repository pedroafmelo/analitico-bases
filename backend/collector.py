import time
import datetime
import decimal
import logging
from datetime import timezone

import pandas as pd

try:
    import pyodbc
except ImportError:
    pyodbc = None

from backend.excel_reader import BaseConfig, ler_configuracoes
from backend.database import (
    buscar_ultima_checagem, salvar_checagem, inicializar_db
)
from backend.health import calcular_status
from backend.query_builder import build_aggregate_query, build_coverage_query

logger = logging.getLogger(__name__)

NUMERIC_TYPES = (int, float, decimal.Decimal)
DATE_TYPES = (datetime.date, datetime.datetime)


def _inferir_tipo(type_code) -> str:
    if type_code in NUMERIC_TYPES:
        return "numérico"
    if type_code in DATE_TYPES:
        return "data"
    return "texto"


def _executar_query(conn, sql: str) -> tuple[str, float, dict | None]:
    """Executa SQL via pd.read_sql, retorna (status_consulta, duracao_seg, row_dict|None)."""
    t0 = time.perf_counter()
    try:
        df = pd.read_sql(sql, conn)
        duracao = time.perf_counter() - t0
        if df.empty:
            return "OK", duracao, {}
        row = df.iloc[0].to_dict()
        return "OK", duracao, row
    except Exception as e:
        duracao = time.perf_counter() - t0
        # Handle pyodbc.OperationalError (timeout)
        if pyodbc is not None and isinstance(e, pyodbc.OperationalError):
            msg = str(e).lower()
            if "timeout" in msg or "timed out" in msg:
                logger.warning("Timeout na query: %s", e)
                return "TIMEOUT", duracao, None
            logger.error("Erro operacional ODBC: %s", e)
            return "ERRO", duracao, None
        # Handle pyodbc.Error (other ODBC errors)
        if pyodbc is not None and isinstance(e, pyodbc.Error):
            sqlstate = e.args[0] if e.args else ""
            if str(sqlstate) == "HY000":
                logger.warning("Resultado incompleto ODBC: %s", e)
                return "INCOMPLETE", duracao, None
            logger.error("Erro ODBC: %s", e)
            return "ERRO", duracao, None
        # Check by class name for when pyodbc is mocked or partially available
        cls_name = type(e).__name__
        if cls_name == "OperationalError":
            msg = str(e).lower()
            if "timeout" in msg or "timed out" in msg:
                logger.warning("Timeout na query: %s", e)
                return "TIMEOUT", duracao, None
            logger.error("Erro operacional: %s", e)
            return "ERRO", duracao, None
        logger.error("Erro ao executar query: %s", e)
        return "ERRO", duracao, None


def coletar_base(config: BaseConfig, db_conn, conn_string: str) -> dict:
    """Conecta via ODBC, coleta métricas, calcula saúde e persiste no SQLite."""
    dt_checagem = datetime.datetime.now(timezone.utc).isoformat()
    anterior = buscar_ultima_checagem(db_conn, config.nome_base)

    if pyodbc is None:
        logger.error("pyodbc não disponível — impossível coletar %s", config.nome_base)
        checagem = _build_erro_checagem(config, dt_checagem, "ERRO", 0.0)
        salvar_checagem(db_conn, checagem, [])
        return checagem

    try:
        with pyodbc.connect(conn_string, timeout=60) as odbc_conn:
            cursor = odbc_conn.cursor()

            # 1. Introspecção de schema
            cursor.execute(f"SELECT * FROM {config.schema_tabela} WHERE 1=0")
            columns = [
                {"nome": col[0], "tipo": _inferir_tipo(col[1])}
                for col in cursor.description
            ]

            # 2. Query agregada principal
            sql_main = build_aggregate_query(config, columns)
            status_consulta, duracao, row_main = _executar_query(odbc_conn, sql_main)

            if status_consulta != "OK" or row_main is None:
                checagem = _build_erro_checagem(
                    config, dt_checagem, status_consulta, duracao
                )
                salvar_checagem(db_conn, checagem, [])
                return checagem

            # 3. Query de cobertura e core
            row_cov = {}
            sql_cov = build_coverage_query(config)
            if sql_cov:
                _, _, row_cov = _executar_query(odbc_conn, sql_cov)
                row_cov = row_cov or {}

            # 4. Métricas atuais
            total_linhas = row_main.get("total_linhas")
            atual = {
                "total_linhas": total_linhas,
                "max_data": str(row_main["max_data"]) if row_main.get("max_data") else None,
                "soma_saldo": row_main.get("soma_saldo"),
            }

            # 5. Saúde
            saude = calcular_status(config, atual, anterior)

            # 6. Métricas por coluna
            metricas = []
            for col in columns:
                nome = col["nome"]
                nulos = row_main.get(f"nulls_{nome}", 0) or 0
                pct = (nulos / total_linhas * 100) if total_linhas else 0.0
                soma = row_main.get(f"sum_{nome}") if col["tipo"] == "numérico" else None
                metricas.append({
                    "nome_coluna": nome,
                    "tipo_dado": col["tipo"],
                    "total_nulos": nulos,
                    "pct_nulos": round(pct, 4),
                    "soma_valor": soma,
                })

            checagem = {
                "nome_base": config.nome_base,
                "dt_checagem": dt_checagem,
                "total_linhas": total_linhas,
                "max_data": atual["max_data"],
                "soma_saldo": atual["soma_saldo"],
                "total_cobertura_base": row_main.get("total_cobertura_base"),
                "total_cobertura_sicredi": row_cov.get("total_cobertura_sicredi"),
                "pct_sicredi": row_cov.get("pct_sicredi"),
                "pct_fisital": row_cov.get("pct_fisital"),
                "pct_woop": row_cov.get("pct_woop"),
                "duracao_query_segundos": round(duracao, 3),
                "status_consulta": "OK",
                **{k: int(v) for k, v in saude.items() if k.startswith("erro_")},
                "status": saude["status"],
            }
            salvar_checagem(db_conn, checagem, metricas)
            return checagem

    except Exception as e:
        logger.error("Erro ao coletar %s: %s", config.nome_base, e)
        checagem = _build_erro_checagem(config, dt_checagem, "ERRO", 0.0)
        salvar_checagem(db_conn, checagem, [])
        return checagem


def _build_erro_checagem(config: BaseConfig, dt_checagem: str, status_consulta: str, duracao: float) -> dict:
    return {
        "nome_base": config.nome_base,
        "dt_checagem": dt_checagem,
        "total_linhas": None, "max_data": None, "soma_saldo": None,
        "total_cobertura_base": None, "total_cobertura_sicredi": None,
        "pct_sicredi": None, "pct_fisital": None, "pct_woop": None,
        "duracao_query_segundos": round(duracao, 3),
        "status_consulta": status_consulta,
        "erro_linhas": 0, "erro_saldo": 0, "erro_data": 0,
        "status": "ERRO",
    }


def coletar_todas(conn_string: str) -> list[dict]:
    db_conn = inicializar_db()
    configs = ler_configuracoes()
    return [coletar_base(cfg, db_conn, conn_string) for cfg in configs]
