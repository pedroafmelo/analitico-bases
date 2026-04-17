from dataclasses import dataclass
from pathlib import Path
import pandas as pd

@dataclass
class BaseConfig:
    nome_base: str
    schema_tabela: str
    filtro_sql: str
    coluna_data: str
    data_evolui: bool
    coluna_saldo: str
    coluna_cobertura: str
    tipo_cobertura: str
    checar_linhas: bool

DEFAULT_PATH = Path(__file__).parent.parent / "data" / "bases_config.xlsx"

def ler_configuracoes(path: Path = DEFAULT_PATH) -> list[BaseConfig]:
    df = pd.read_excel(path, dtype=str).fillna("")
    configs = []
    for _, row in df.iterrows():
        configs.append(BaseConfig(
            nome_base=row["nome_base"].strip(),
            schema_tabela=row["schema_tabela"].strip(),
            filtro_sql=row["filtro_sql"].strip(),
            coluna_data=row["coluna_data"].strip(),
            data_evolui=row["data_evolui"].strip().lower() == "sim",
            coluna_saldo=row["coluna_saldo"].strip(),
            coluna_cobertura=row["coluna_cobertura"].strip(),
            tipo_cobertura=row["tipo_cobertura"].strip().lower(),
            checar_linhas=row["checar_linhas"].strip().lower() == "sim",
        ))
    return configs
