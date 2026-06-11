import azure.functions as func
import logging
import os
import pyodbc

app = func.Blueprint()

@app.timer_trigger(schedule="0 5 6 * * *", arg_name="timer", run_on_startup=False)
def extract_representante(timer: func.TimerRequest) -> None:

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
        rows = src.cursor().execute("SELECT * FROM erp.representante").fetchall()
        logging.info(f"representante: {len(rows)} registros lidos")

        dest_cursor = dest.cursor()
        for row in rows:
            dest_cursor.execute("""
                MERGE dbo.representante AS t
                USING (VALUES (?, ?, ?, ?, ?)) AS s (cd_representante, nm_representante, ds_email, ds_telefone, id_regiao)
                ON t.cd_representante = s.cd_representante
                WHEN MATCHED THEN UPDATE SET t.nm_representante = s.nm_representante, t.ds_email = s.ds_email, t.ds_telefone = s.ds_telefone, t.id_regiao = s.id_regiao
                WHEN NOT MATCHED THEN INSERT (cd_representante, nm_representante, ds_email, ds_telefone, id_regiao) VALUES (s.cd_representante, s.nm_representante, s.ds_email, s.ds_telefone, s.id_regiao);
            """, row.cd_representante, row.nm_representante, row.ds_email, row.ds_telefone, row.id_regiao)
        dest.commit()
        logging.info("representante: carga concluída")

    except Exception as e:
        logging.error(f"Erro em representante: {e}")
        raise
    finally:
        src.close()
        dest.close()