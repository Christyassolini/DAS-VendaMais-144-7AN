import azure.functions as func
import logging
import os
import pyodbc

app = func.Blueprint()

@app.timer_trigger(schedule="0 5 6 * * *", arg_name="timer", run_on_startup=False)
def extract_cliente(timer: func.TimerRequest) -> None:

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
        rows = src.cursor().execute("SELECT * FROM erp.cliente").fetchall()
        logging.info(f"cliente: {len(rows)} registros lidos")

        dest_cursor = dest.cursor()
        for row in rows:
            dest_cursor.execute("""
                MERGE dbo.cliente AS t
                USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?)) AS s (cd_cliente, nm_cliente, tp_pessoa, nr_cnpj_cpf, ds_email, ds_telefone, id_regiao, id_representante)
                ON t.cd_cliente = s.cd_cliente
                WHEN MATCHED THEN UPDATE SET t.nm_cliente = s.nm_cliente, t.tp_pessoa = s.tp_pessoa, t.nr_cnpj_cpf = s.nr_cnpj_cpf, t.ds_email = s.ds_email, t.ds_telefone = s.ds_telefone, t.id_regiao = s.id_regiao, t.id_representante = s.id_representante
                WHEN NOT MATCHED THEN INSERT (cd_cliente, nm_cliente, tp_pessoa, nr_cnpj_cpf, ds_email, ds_telefone, id_regiao, id_representante) VALUES (s.cd_cliente, s.nm_cliente, s.tp_pessoa, s.nr_cnpj_cpf, s.ds_email, s.ds_telefone, s.id_regiao, s.id_representante);
            """, row.cd_cliente, row.nm_cliente, row.tp_pessoa, row.nr_cnpj_cpf, row.ds_email, row.ds_telefone, row.id_regiao, row.id_representante)
        dest.commit()
        logging.info("cliente: carga concluída")

    except Exception as e:
        logging.error(f"Erro em cliente: {e}")
        raise
    finally:
        src.close()
        dest.close()