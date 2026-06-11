import azure.functions as func
import logging
import os
import pyodbc

app = func.Blueprint()

@app.timer_trigger(schedule="0 5 6 * * *", arg_name="timer", run_on_startup=False)
def extract_produto(timer: func.TimerRequest) -> None:

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
        rows = src.cursor().execute("SELECT * FROM erp.produto").fetchall()
        logging.info(f"produto: {len(rows)} registros lidos")

        dest_cursor = dest.cursor()
        for row in rows:
            dest_cursor.execute("""
                MERGE dbo.produto AS t
                USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS s (cd_produto, cd_sku, nm_produto, id_categoria, nm_unidade_medida, qt_ponto_reposicao, fl_ativo, dt_atualizacao, nm_sistema_origem, cd_registro_origem)
                ON t.cd_sku = s.cd_sku
                WHEN MATCHED THEN UPDATE SET
                    t.cd_produto = s.cd_produto, t.nm_produto = s.nm_produto,
                    t.id_categoria = s.id_categoria, t.nm_unidade_medida = s.nm_unidade_medida,
                    t.qt_ponto_reposicao = s.qt_ponto_reposicao, t.fl_ativo = s.fl_ativo,
                    t.dt_atualizacao = s.dt_atualizacao, t.nm_sistema_origem = s.nm_sistema_origem,
                    t.cd_registro_origem = s.cd_registro_origem
                WHEN NOT MATCHED THEN INSERT (cd_produto, cd_sku, nm_produto, id_categoria, nm_unidade_medida, qt_ponto_reposicao, fl_ativo, dt_atualizacao, nm_sistema_origem, cd_registro_origem)
                VALUES (s.cd_produto, s.cd_sku, s.nm_produto, s.id_categoria, s.nm_unidade_medida, s.qt_ponto_reposicao, s.fl_ativo, s.dt_atualizacao, s.nm_sistema_origem, s.cd_registro_origem);
            """, row.cd_produto, row.cd_sku, row.nm_produto, row.id_categoria, row.nm_unidade_medida, row.qt_ponto_reposicao, row.fl_ativo, row.dt_atualizacao, row.nm_sistema_origem, row.cd_registro_origem)
        dest.commit()
        logging.info("produto: carga concluída")

    except Exception as e:
        logging.error(f"Erro em produto: {e}")
        raise
    finally:
        src.close()
        dest.close()