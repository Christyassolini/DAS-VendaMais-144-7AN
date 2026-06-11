import azure.functions as func
import logging
import os
import pyodbc

app = func.Blueprint()

@app.timer_trigger(schedule="0 0 6 * * *", arg_name="timer", run_on_startup=False)
def extract_categoria_produto(timer: func.TimerRequest) -> None:

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
        rows = src.cursor().execute("SELECT * FROM erp.categoria_produto").fetchall()
        logging.info(f"categoria_produto: {len(rows)} registros lidos")

        dest_cursor = dest.cursor()
        for row in rows:
            dest_cursor.execute("""
                MERGE dbo.categoria_produto AS t
                USING (VALUES (?, ?, ?, ?, ?, ?)) AS s (cd_categoria, nm_categoria, fl_ativo, dt_atualizacao, nm_sistema_origem, cd_registro_origem)
                ON t.cd_categoria = s.cd_categoria
                WHEN MATCHED THEN UPDATE SET
                    t.nm_categoria = s.nm_categoria, t.fl_ativo = s.fl_ativo,
                    t.dt_atualizacao = s.dt_atualizacao, t.nm_sistema_origem = s.nm_sistema_origem,
                    t.cd_registro_origem = s.cd_registro_origem
                WHEN NOT MATCHED THEN INSERT (cd_categoria, nm_categoria, fl_ativo, dt_atualizacao, nm_sistema_origem, cd_registro_origem)
                VALUES (s.cd_categoria, s.nm_categoria, s.fl_ativo, s.dt_atualizacao, s.nm_sistema_origem, s.cd_registro_origem);
            """, row.cd_categoria, row.nm_categoria, row.fl_ativo, row.dt_atualizacao, row.nm_sistema_origem, row.cd_registro_origem)
        dest.commit()
        logging.info("categoria_produto: carga concluída")

    except Exception as e:
        logging.error(f"Erro em categoria_produto: {e}")
        raise
    finally:
        src.close()
        dest.close()