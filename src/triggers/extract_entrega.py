import azure.functions as func
import logging
import os
import pyodbc

app = func.Blueprint()

@app.timer_trigger(schedule="0 15 6 * * *", arg_name="timer", run_on_startup=False)
def extract_entrega(timer: func.TimerRequest) -> None:

    src = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={os.getenv('SQL_SERVER_SOURCE')};"
        f"DATABASE={os.getenv('SQL_DATABASE_SOURCE')};"
        f"UID={os.getenv('SQL_USER_SOURCE')};"
        f"PWD={os.getenv('SQL_PASSWORD_SOURCE')};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    dest = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={os.getenv('SQL_SERVER_DEST')};"
        f"DATABASE={os.getenv('SQL_DATABASE_DEST')};"
        f"UID={os.getenv('SQL_USER_DEST')};"
        f"PWD={os.getenv('SQL_PASSWORD_DEST')};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )

    try:
        rows = src.cursor().execute("SELECT * FROM erp.entrega").fetchall()
        logging.info(f"entrega: {len(rows)} registros lidos")

        dest_cursor = dest.cursor()
        for row in rows:
            dest_cursor.execute("""
                MERGE dbo.entrega AS t
                USING (VALUES (?, ?, ?, ?, ?, ?)) AS s (id_pedido, id_transportadora, id_regiao, dt_prometida, dt_entrega, ds_status_entrega)
                ON t.id_pedido = s.id_pedido
                WHEN MATCHED THEN UPDATE SET t.id_transportadora = s.id_transportadora, t.dt_prometida = s.dt_prometida, t.dt_entrega = s.dt_entrega, t.ds_status_entrega = s.ds_status_entrega
                WHEN NOT MATCHED THEN INSERT (id_pedido, id_transportadora, id_regiao, dt_prometida, dt_entrega, ds_status_entrega) VALUES (s.id_pedido, s.id_transportadora, s.id_regiao, s.dt_prometida, s.dt_entrega, s.ds_status_entrega);
            """, row.id_pedido, row.id_transportadora, row.id_regiao, row.dt_prometida, row.dt_entrega, row.ds_status_entrega)
        dest.commit()
        logging.info("entrega: carga concluída")

    except Exception as e:
        logging.error(f"Erro em entrega: {e}")
        raise
    finally:
        src.close()
        dest.close()