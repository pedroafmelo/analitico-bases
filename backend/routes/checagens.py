from fastapi import APIRouter
from backend.database import get_connection, buscar_historico

router = APIRouter()

@router.get("/bases/{nome}/historico")
def get_historico(nome: str, limit: int = 30):
    conn = get_connection()
    historico = buscar_historico(conn, nome, limit)
    return historico
