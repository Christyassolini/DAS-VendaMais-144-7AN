import azure.functions as func
import logging
import os
import pyodbc

app = func.Blueprint()

@app.timer_trigger(schedule="0 15 6 * * *", arg_name="timer", run_on_startup=False)
def extract_titulo_receber(timer: func.TimerRequest) -> None:

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
        rows = src.cursor().execute("SELECT * FROM erp.titulo_receber").fetchall()
        logging.info(f"titulo_receber: {len(rows)} registros lidos")

        dest_cursor = dest.cursor()
        for row in rows:
            dest_cursor.execute("""
                MERGE dbo.titulo_receber AS t
                USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?)) AS s (nr_titulo, id_cliente, id_pedido, dt_emissao, dt_vencimento, dt_pagamento, vl_titulo, ds_status_titulo)
                ON t.nr_titulo = s.nr_titulo
                WHEN MATCHED THEN UPDATE SET t.dt_pagamento = s.dt_pagamento, t.vl_titulo = s.vl_titulo, t.ds_status_titulo = s.ds_status_titulo
                WHEN NOT MATCHED THEN INSERT (nr_titulo, id_cliente, id_pedido, dt_emissao, dt_vencimento, dt_pagamento, vl_titulo, ds_status_titulo) VALUES (s.nr_titulo, s.id_cliente, s.id_pedido, s.dt_emissao, s.dt_vencimento, s.dt_pagamento, s.vl_titulo, s.ds_status_titulo);
            """, row.nr_titulo, row.id_cliente, row.id_pedido, row.dt_emissao, row.dt_vencimento, row.dt_pagamento, row.vl_titulo, row.ds_status_titulo)
        dest.commit()
        logging.info("titulo_receber: carga concluída")

    except Exception as e:
        logging.error(f"Erro em titulo_receber: {e}")
        raise
    finally:
        src.close()
        dest.close()