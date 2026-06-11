import azure.functions as func
import logging
import os
import pyodbc

app = func.Blueprint()

@app.timer_trigger(schedule="0 5 6 * * *", arg_name="timer", run_on_startup=False)
def extract_produto(timer: func.TimerRequest) -> None:

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
        rows = src.cursor().execute("SELECT * FROM erp.produto").fetchall()
        logging.info(f"produto: {len(rows)} registros lidos")

        dest_cursor = dest.cursor()
        for row in rows:
            dest_cursor.execute("""
                MERGE dbo.produto AS t
                USING (VALUES (?, ?, ?, ?, ?)) AS s (cd_sku, cd_produto, nm_produto, id_categoria, nm_unidade_medida)
                ON t.cd_sku = s.cd_sku
                WHEN MATCHED THEN UPDATE SET t.cd_produto = s.cd_produto, t.nm_produto = s.nm_produto, t.id_categoria = s.id_categoria, t.nm_unidade_medida = s.nm_unidade_medida
                WHEN NOT MATCHED THEN INSERT (cd_sku, cd_produto, nm_produto, id_categoria, nm_unidade_medida) VALUES (s.cd_sku, s.cd_produto, s.nm_produto, s.id_categoria, s.nm_unidade_medida);
            """, row.cd_sku, row.cd_produto, row.nm_produto, row.id_categoria, row.nm_unidade_medida)
        dest.commit()
        logging.info("produto: carga concluída")

    except Exception as e:
        logging.error(f"Erro em produto: {e}")
        raise
    finally:
        src.close()
        dest.close()