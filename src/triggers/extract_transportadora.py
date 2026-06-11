import azure.functions as func
import logging
import os
import pyodbc

app = func.Blueprint()

@app.timer_trigger(schedule="0 0 6 * * *", arg_name="timer", run_on_startup=False)
def extract_transportadora(timer: func.TimerRequest) -> None:

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
        rows = src.cursor().execute("SELECT * FROM erp.transportadora").fetchall()
        logging.info(f"transportadora: {len(rows)} registros lidos")

        dest_cursor = dest.cursor()
        for row in rows:
            dest_cursor.execute("""
                MERGE dbo.transportadora AS t
                USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?)) AS s (cd_transportadora, nm_transportadora, nr_cnpj, ds_telefone, fl_ativo, dt_atualizacao, nm_sistema_origem, cd_registro_origem)
                ON t.cd_transportadora = s.cd_transportadora
                WHEN MATCHED THEN UPDATE SET
                    t.nm_transportadora = s.nm_transportadora, t.nr_cnpj = s.nr_cnpj,
                    t.ds_telefone = s.ds_telefone, t.fl_ativo = s.fl_ativo,
                    t.dt_atualizacao = s.dt_atualizacao, t.nm_sistema_origem = s.nm_sistema_origem,
                    t.cd_registro_origem = s.cd_registro_origem
                WHEN NOT MATCHED THEN INSERT (cd_transportadora, nm_transportadora, nr_cnpj, ds_telefone, fl_ativo, dt_atualizacao, nm_sistema_origem, cd_registro_origem)
                VALUES (s.cd_transportadora, s.nm_transportadora, s.nr_cnpj, s.ds_telefone, s.fl_ativo, s.dt_atualizacao, s.nm_sistema_origem, s.cd_registro_origem);
            """, row.cd_transportadora, row.nm_transportadora, row.nr_cnpj, row.ds_telefone, row.fl_ativo, row.dt_atualizacao, row.nm_sistema_origem, row.cd_registro_origem)
        dest.commit()
        logging.info("transportadora: carga concluída")

    except Exception as e:
        logging.error(f"Erro em transportadora: {e}")
        raise
    finally:
        src.close()
        dest.close()