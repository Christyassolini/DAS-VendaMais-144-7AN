import azure.functions as func
import logging
import os
import pyodbc

app = func.Blueprint()

@app.timer_trigger(schedule="0 20 6 * * *", arg_name="timer", run_on_startup=False)
def extract_estoque_movimento(timer: func.TimerRequest) -> None:

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
        rows = src.cursor().execute("SELECT * FROM erp.estoque_movimentacao").fetchall()
        logging.info(f"estoque_movimentacao: {len(rows)} registros lidos")

        dest_cursor = dest.cursor()
        for row in rows:
            dest_cursor.execute("""
                MERGE dbo.estoque_movimentacao AS t
                USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)) AS s (id_produto, dt_movimentacao, ds_tipo_movimentacao, qt_movimentacao, nr_documento_origem, id_pedido, ds_observacao, dt_atualizacao, nm_sistema_origem)
                ON t.id_produto = s.id_produto AND t.dt_movimentacao = s.dt_movimentacao AND t.nr_documento_origem = s.nr_documento_origem
                WHEN NOT MATCHED THEN INSERT (id_produto, dt_movimentacao, ds_tipo_movimentacao, qt_movimentacao, nr_documento_origem, id_pedido, ds_observacao, dt_atualizacao, nm_sistema_origem)
                VALUES (s.id_produto, s.dt_movimentacao, s.ds_tipo_movimentacao, s.qt_movimentacao, s.nr_documento_origem, s.id_pedido, s.ds_observacao, s.dt_atualizacao, s.nm_sistema_origem);
            """, row.id_produto, row.dt_movimentacao, row.ds_tipo_movimentacao, row.qt_movimentacao, row.nr_documento_origem, row.id_pedido, row.ds_observacao, row.dt_atualizacao, row.nm_sistema_origem)
        dest.commit()
        logging.info("estoque_movimentacao: carga concluída")

    except Exception as e:
        logging.error(f"Erro em estoque_movimentacao: {e}")
        raise
    finally:
        src.close()
        dest.close()