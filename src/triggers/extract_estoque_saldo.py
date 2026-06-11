import azure.functions as func
import logging
import os
import pyodbc

app = func.Blueprint()

@app.timer_trigger(schedule="0 20 6 * * *", arg_name="timer", run_on_startup=False)
def extract_estoque_saldo(timer: func.TimerRequest) -> None:

    src = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={os.getenv('SQL_SERVER_SOURCE')};DATABASE={os.getenv('SQL_DATABASE_SOURCE')};"
        f"UID={os.getenv('SQL_USER_SOURCE')};PWD={os.getenv('SQL_PASSWORD_SOURCE')};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    dest = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={os.getenv('SQL_SERVER_DEST')};DATABASE={os.getenv('SQL_DATABASE_DEST')};"
        f"UID={os.getenv('SQL_USER_DEST')};PWD={os.getenv('SQL_PASSWORD_DEST')};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )

    try:
        rows = src.cursor().execute("SELECT * FROM erp.estoque_saldo").fetchall()
        logging.info(f"estoque_saldo: {len(rows)} registros lidos")

        dest_cursor = dest.cursor()
        for row in rows:
            dest_cursor.execute("""
                MERGE dbo.estoque_saldo AS t
                USING (VALUES (?, ?, ?, ?, ?)) AS s (id_produto, dt_referencia, qt_saldo, dt_atualizacao, nm_sistema_origem)
                ON t.id_produto = s.id_produto AND t.dt_referencia = s.dt_referencia
                WHEN MATCHED THEN UPDATE SET
                    t.qt_saldo = s.qt_saldo, t.dt_atualizacao = s.dt_atualizacao,
                    t.nm_sistema_origem = s.nm_sistema_origem
                WHEN NOT MATCHED THEN INSERT (id_produto, dt_referencia, qt_saldo, dt_atualizacao, nm_sistema_origem)
                VALUES (s.id_produto, s.dt_referencia, s.qt_saldo, s.dt_atualizacao, s.nm_sistema_origem);
            """, row.id_produto, row.dt_referencia, row.qt_saldo, row.dt_atualizacao, row.nm_sistema_origem)
        dest.commit()
        logging.info("estoque_saldo: carga concluída")

    except Exception as e:
        logging.error(f"Erro em estoque_saldo: {e}")
        raise
    finally:
        src.close()
        dest.close()