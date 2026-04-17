#!/usr/bin/env python3
"""
CLI para coleta diária de métricas das bases.
Uso:
  python collect.py                  # sonda todas as bases
  python collect.py --base nome_base # sonda uma base específica
"""
import argparse
import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

def main():
    parser = argparse.ArgumentParser(description="DB Health Monitor — coleta de métricas")
    parser.add_argument("--base", help="Nome da base a sondar (omitir para sondar todas)")
    args = parser.parse_args()

    conn_string = os.getenv("ODBC_CONNECTION_STRING")
    if not conn_string:
        print("ERRO: variável ODBC_CONNECTION_STRING não definida no .env")
        sys.exit(1)

    from backend.database import inicializar_db
    from backend.excel_reader import ler_configuracoes
    from backend.collector import coletar_base

    db_conn = inicializar_db()
    configs = ler_configuracoes()

    if args.base:
        config = next((c for c in configs if c.nome_base == args.base), None)
        if not config:
            print(f"ERRO: base '{args.base}' não encontrada no Excel de configuração")
            sys.exit(1)
        resultado = coletar_base(config, db_conn, conn_string)
        print(f"[{resultado['nome_base']}] status={resultado['status']} consulta={resultado['status_consulta']} linhas={resultado['total_linhas']}")
    else:
        for config in configs:
            resultado = coletar_base(config, db_conn, conn_string)
            print(f"[{resultado['nome_base']}] status={resultado['status']} consulta={resultado['status_consulta']} linhas={resultado['total_linhas']}")

if __name__ == "__main__":
    main()
