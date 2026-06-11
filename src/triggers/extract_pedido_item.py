import azure.functions as func
import logging
import os
import pyodbc

app = func.Blueprint()

@app.timer_trigger(schedule="0 15 6 * * *", arg_name="timer", run_on_startup=False)
def extract_pedido_item(timer: func.TimerRequest) -> None:

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
        rows = src.cursor().execute("SELECT * FROM erp.pedido_item").fetchall()
        logging.info(f"pedido_item: {len(rows)} registros lidos")

        dest_cursor = dest.cursor()
        for row in rows:
            dest_cursor.execute("""
                MERGE dbo.pedido_item AS t
                USING (VALUES (?, ?, ?, ?, ?, ?, ?)) AS s (id_pedido, nr_sequencia_item, id_produto, qt_item, vl_preco_unitario, vl_bruto, vl_liquido)
                ON t.id_pedido = s.id_pedido AND t.nr_sequencia_item = s.nr_sequencia_item
                WHEN MATCHED THEN UPDATE SET t.qt_item = s.qt_item, t.vl_preco_unitario = s.vl_preco_unitario, t.vl_bruto = s.vl_bruto, t.vl_liquido = s.vl_liquido
                WHEN NOT MATCHED THEN INSERT (id_pedido, nr_sequencia_item, id_produto, qt_item, vl_preco_unitario, vl_bruto, vl_liquido) VALUES (s.id_pedido, s.nr_sequencia_item, s.id_produto, s.qt_item, s.vl_preco_unitario, s.vl_bruto, s.vl_liquido);
            """, row.id_pedido, row.nr_sequencia_item, row.id_produto, row.qt_item, row.vl_preco_unitario, row.vl_bruto, row.vl_liquido)
        dest.commit()
        logging.info("pedido_item: carga concluída")

    except Exception as e:
        logging.error(f"Erro em pedido_item: {e}")
        raise
    finally:
        src.close()
        dest.close()