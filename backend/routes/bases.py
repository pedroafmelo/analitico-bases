from fastapi import APIRouter, HTTPException
from backend.database import get_connection, listar_bases, buscar_ultima_checagem, buscar_metricas_colunas

router = APIRouter()

@router.get("/bases")
def get_bases():
    conn = get_connection()
    return listar_bases(conn)

@router.get("/bases/{nome}")
def get_base(nome: str):
    conn = get_connection()
    checagem = buscar_ultima_checagem(conn, nome)
    if not checagem:
        raise HTTPException(status_code=404, detail="Base não encontrada")
    metricas = buscar_metricas_colunas(conn, checagem["id"])
    return {**checagem, "metricas_colunas": metricas}
