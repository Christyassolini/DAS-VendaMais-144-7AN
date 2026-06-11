import azure.functions as func
import logging
import os
import pyodbc

app = func.Blueprint()

@app.timer_trigger(schedule="0 15 6 * * *", arg_name="timer", run_on_startup=False)
def extract_pedido(timer: func.TimerRequest) -> None:

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
        rows = src.cursor().execute("SELECT * FROM erp.pedido").fetchall()
        logging.info(f"pedido: {len(rows)} registros lidos")

        dest_cursor = dest.cursor()
        for row in rows:
            dest_cursor.execute("""
                MERGE dbo.pedido AS t
                USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS s (nr_pedido, id_cliente, id_representante, id_regiao, dt_emissao, dt_faturamento, ds_status_pedido, vl_bruto, vl_desconto, vl_liquido, ds_observacao, dt_atualizacao, nm_sistema_origem, cd_registro_origem)
                ON t.nr_pedido = s.nr_pedido
                WHEN MATCHED THEN UPDATE SET
                    t.id_cliente = s.id_cliente, t.id_representante = s.id_representante,
                    t.id_regiao = s.id_regiao, t.dt_emissao = s.dt_emissao,
                    t.dt_faturamento = s.dt_faturamento, t.ds_status_pedido = s.ds_status_pedido,
                    t.vl_bruto = s.vl_bruto, t.vl_desconto = s.vl_desconto,
                    t.vl_liquido = s.vl_liquido, t.ds_observacao = s.ds_observacao,
                    t.dt_atualizacao = s.dt_atualizacao, t.nm_sistema_origem = s.nm_sistema_origem,
                    t.cd_registro_origem = s.cd_registro_origem
                WHEN NOT MATCHED THEN INSERT (nr_pedido, id_cliente, id_representante, id_regiao, dt_emissao, dt_faturamento, ds_status_pedido, vl_bruto, vl_desconto, vl_liquido, ds_observacao, dt_atualizacao, nm_sistema_origem, cd_registro_origem)
                VALUES (s.nr_pedido, s.id_cliente, s.id_representante, s.id_regiao, s.dt_emissao, s.dt_faturamento, s.ds_status_pedido, s.vl_bruto, s.vl_desconto, s.vl_liquido, s.ds_observacao, s.dt_atualizacao, s.nm_sistema_origem, s.cd_registro_origem);
            """, row.nr_pedido, row.id_cliente, row.id_representante, row.id_regiao, row.dt_emissao, row.dt_faturamento, row.ds_status_pedido, row.vl_bruto, row.vl_desconto, row.vl_liquido, row.ds_observacao, row.dt_atualizacao, row.nm_sistema_origem, row.cd_registro_origem)
        dest.commit()
        logging.info("pedido: carga concluída")

    except Exception as e:
        logging.error(f"Erro em pedido: {e}")
        raise
    finally:
        src.close()
        dest.close()