import azure.functions as func
import logging
import os
import pyodbc

app = func.Blueprint()

@app.timer_trigger(schedule="0 0 6 * * *", arg_name="timer", run_on_startup=False)
def extract_regiao(timer: func.TimerRequest) -> None:

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
        rows = src.cursor().execute("SELECT * FROM erp.regiao").fetchall()
        logging.info(f"regiao: {len(rows)} registros lidos")

        dest_cursor = dest.cursor()
        for row in rows:
            dest_cursor.execute("""
                MERGE dbo.regiao AS t
                USING (VALUES (?, ?, ?, ?)) AS s (cd_regiao, nm_regiao, sg_uf, nm_cidade)
                ON t.cd_regiao = s.cd_regiao
                WHEN MATCHED THEN UPDATE SET t.nm_regiao = s.nm_regiao, t.sg_uf = s.sg_uf, t.nm_cidade = s.nm_cidade
                WHEN NOT MATCHED THEN INSERT (cd_regiao, nm_regiao, sg_uf, nm_cidade) VALUES (s.cd_regiao, s.nm_regiao, s.sg_uf, s.nm_cidade);
            """, row.cd_regiao, row.nm_regiao, row.sg_uf, row.nm_cidade)
        dest.commit()
        logging.info("regiao: carga concluída")

    except Exception as e:
        logging.error(f"Erro em regiao: {e}")
        raise
    finally:
        src.close()
        dest.close()