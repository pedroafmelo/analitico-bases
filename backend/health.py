from backend.excel_reader import BaseConfig

def calcular_status(config: BaseConfig, atual: dict, anterior: dict | None) -> dict:
    """
    Compara métricas atuais com as anteriores e retorna flags de erro e status.
    atual e anterior são dicts com chaves: total_linhas, max_data, soma_saldo.
    anterior=None indica primeira checagem.
    """
    if anterior is None:
        return {
            "erro_linhas": False,
            "erro_saldo": False,
            "erro_data": False,
            "status": "PRIMEIRO_CHECK",
        }

    erro_linhas = _verificar_variacao(
        atual.get("total_linhas"),
        anterior.get("total_linhas"),
        ativo=config.checar_linhas,
    )

    erro_saldo = _verificar_variacao(
        atual.get("soma_saldo"),
        anterior.get("soma_saldo"),
        ativo=config.coluna_saldo != "sem_coluna",
    )

    erro_data = _verificar_data(
        atual.get("max_data"),
        anterior.get("max_data"),
        ativo=config.coluna_data != "sem_coluna",
        deve_evoluir=config.data_evolui,
    )

    status = "ERRO" if (erro_linhas or erro_saldo or erro_data) else "OK"
    return {
        "erro_linhas": erro_linhas,
        "erro_saldo": erro_saldo,
        "erro_data": erro_data,
        "status": status,
    }

def _verificar_variacao(atual, anterior, ativo: bool) -> bool:
    if not ativo or atual is None or not anterior:
        return False
    ratio = atual / anterior
    return ratio < 0.8 or ratio > 1.2

def _verificar_data(atual: str | None, anterior: str | None, ativo: bool, deve_evoluir: bool) -> bool:
    if not ativo or not atual or not anterior:
        return False
    if deve_evoluir:
        return atual <= anterior
    else:
        return atual < anterior
