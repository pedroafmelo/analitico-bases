import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "historico.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabelas(conn: sqlite3.Connection) -> None:
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS checagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_base TEXT NOT NULL,
        dt_checagem TEXT NOT NULL,
        total_linhas INTEGER,
        max_data TEXT,
        soma_saldo REAL,
        total_cobertura_base INTEGER,
        total_cobertura_sicredi INTEGER,
        pct_sicredi REAL,
        pct_fisital REAL,
        pct_woop REAL,
        duracao_query_segundos REAL,
        status_consulta TEXT NOT NULL,
        erro_linhas INTEGER NOT NULL DEFAULT 0,
        erro_saldo INTEGER NOT NULL DEFAULT 0,
        erro_data INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS metricas_colunas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        checagem_id INTEGER NOT NULL REFERENCES checagens(id),
        nome_coluna TEXT NOT NULL,
        tipo_dado TEXT NOT NULL,
        total_nulos INTEGER,
        pct_nulos REAL,
        soma_valor REAL
    );
    """)
    conn.commit()

def salvar_checagem(conn: sqlite3.Connection, checagem: dict, metricas: list[dict]) -> int:
    cur = conn.execute("""
        INSERT INTO checagens (
            nome_base, dt_checagem, total_linhas, max_data, soma_saldo,
            total_cobertura_base, total_cobertura_sicredi,
            pct_sicredi, pct_fisital, pct_woop,
            duracao_query_segundos, status_consulta,
            erro_linhas, erro_saldo, erro_data, status
        ) VALUES (
            :nome_base, :dt_checagem, :total_linhas, :max_data, :soma_saldo,
            :total_cobertura_base, :total_cobertura_sicredi,
            :pct_sicredi, :pct_fisital, :pct_woop,
            :duracao_query_segundos, :status_consulta,
            :erro_linhas, :erro_saldo, :erro_data, :status
        )
    """, checagem)
    checagem_id = cur.lastrowid
    for m in metricas:
        conn.execute("""
            INSERT INTO metricas_colunas (checagem_id, nome_coluna, tipo_dado, total_nulos, pct_nulos, soma_valor)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (checagem_id, m["nome_coluna"], m["tipo_dado"], m["total_nulos"], m["pct_nulos"], m["soma_valor"]))
    conn.commit()
    return checagem_id

def buscar_ultima_checagem(conn: sqlite3.Connection, nome_base: str) -> dict | None:
    row = conn.execute(
        "SELECT * FROM checagens WHERE nome_base = ? ORDER BY dt_checagem DESC LIMIT 1",
        (nome_base,)
    ).fetchone()
    return dict(row) if row else None

def listar_bases(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("""
        SELECT c.* FROM checagens c
        INNER JOIN (
            SELECT nome_base, MAX(dt_checagem) as max_dt
            FROM checagens GROUP BY nome_base
        ) latest ON c.nome_base = latest.nome_base AND c.dt_checagem = latest.max_dt
        ORDER BY c.nome_base
    """).fetchall()
    return [dict(r) for r in rows]

def buscar_historico(conn: sqlite3.Connection, nome_base: str, limit: int = 30) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM checagens WHERE nome_base = ? ORDER BY dt_checagem DESC LIMIT ?",
        (nome_base, limit)
    ).fetchall()
    return [dict(r) for r in reversed(rows)]

def buscar_metricas_colunas(conn: sqlite3.Connection, checagem_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM metricas_colunas WHERE checagem_id = ?", (checagem_id,)
    ).fetchall()
    return [dict(r) for r in rows]

def inicializar_db() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    criar_tabelas(conn)
    return conn
