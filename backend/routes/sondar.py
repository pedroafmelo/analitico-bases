import os
from fastapi import APIRouter, BackgroundTasks, HTTPException
from backend.database import get_connection
from backend.collector import coletar_base, coletar_todas
from backend.excel_reader import ler_configuracoes

router = APIRouter()

def _conn_string() -> str:
    cs = os.getenv("ODBC_CONNECTION_STRING", "")
    if not cs:
        raise HTTPException(status_code=500, detail="ODBC_CONNECTION_STRING não configurada")
    return cs

@router.post("/sondar")
def sondar_todas(background_tasks: BackgroundTasks):
    cs = _conn_string()
    background_tasks.add_task(coletar_todas, cs)
    return {"message": "Sondagem iniciada para todas as bases"}

@router.post("/sondar/{nome}")
def sondar_base(nome: str, background_tasks: BackgroundTasks):
    cs = _conn_string()
    configs = ler_configuracoes()
    config = next((c for c in configs if c.nome_base == nome), None)
    if not config:
        raise HTTPException(status_code=404, detail=f"Base '{nome}' não encontrada no Excel")
    db_conn = get_connection()
    background_tasks.add_task(coletar_base, config, db_conn, cs)
    return {"message": f"Sondagem iniciada para '{nome}'"}
