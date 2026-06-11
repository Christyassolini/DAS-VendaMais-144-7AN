import azure.functions as func
import logging
import os
import pyodbc

app = func.Blueprint()

@app.timer_trigger(schedule="0 20 6 * * *", arg_name="timer", run_on_startup=False)
def extract_entrega(timer: func.TimerRequest) -> None:

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
        rows = src.cursor().execute("SELECT * FROM erp.entrega").fetchall()
        logging.info(f"entrega: {len(rows)} registros lidos")

        dest_cursor = dest.cursor()
        for row in rows:
            dest_cursor.execute("""
                MERGE dbo.entrega AS t
                USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS s (id_pedido, id_transportadora, id_regiao, dt_prometida, dt_entrega, ds_status_entrega, cd_rastreio, ds_observacao, dt_atualizacao, nm_sistema_origem)
                ON t.id_pedido = s.id_pedido
                WHEN MATCHED THEN UPDATE SET
                    t.id_transportadora = s.id_transportadora, t.id_regiao = s.id_regiao,
                    t.dt_prometida = s.dt_prometida, t.dt_entrega = s.dt_entrega,
                    t.ds_status_entrega = s.ds_status_entrega, t.cd_rastreio = s.cd_rastreio,
                    t.ds_observacao = s.ds_observacao, t.dt_atualizacao = s.dt_atualizacao,
                    t.nm_sistema_origem = s.nm_sistema_origem
                WHEN NOT MATCHED THEN INSERT (id_pedido, id_transportadora, id_regiao, dt_prometida, dt_entrega, ds_status_entrega, cd_rastreio, ds_observacao, dt_atualizacao, nm_sistema_origem)
                VALUES (s.id_pedido, s.id_transportadora, s.id_regiao, s.dt_prometida, s.dt_entrega, s.ds_status_entrega, s.cd_rastreio, s.ds_observacao, s.dt_atualizacao, s.nm_sistema_origem);
            """, row.id_pedido, row.id_transportadora, row.id_regiao, row.dt_prometida, row.dt_entrega, row.ds_status_entrega, row.cd_rastreio, row.ds_observacao, row.dt_atualizacao, row.nm_sistema_origem)
        dest.commit()
        logging.info("entrega: carga concluída")

    except Exception as e:
        logging.error(f"Erro em entrega: {e}")
        raise
    finally:
        src.close()
        dest.close()