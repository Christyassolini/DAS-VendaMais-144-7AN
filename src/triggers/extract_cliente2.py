import azure.functions as func
import logging
import os
import urllib

app = func.Blueprint()

@app.timer_trigger(schedule="0 0 6 * * *", arg_name="timer", run_on_startup=False)
def extract_cliente(timer: func.TimerRequest) -> None:

    sql_server = os.getenv("SQL_SERVER_SOURCE")
    sql_database = os.getenv("SQL_DATABASE_SOURCE")
    sql_user = os.getenv("SQL_USER_SOURCE")
    sql_pass = os.getenv("SQL_PASSWORD_SOURCE")

    logging.info(f"sql_server:{sql_server}, database:{sql_database}, user:{sql_user}, password:{sql_pass}...")

    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={sql_server};"
        f"DATABASE={sql_database};"
        f"UID={sql_user};"
        f"PWD={sql_pass};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    try:

        params = urllib.parse.quote_plus(conn_str)
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

        with engine.connect() as conn:
            query = text("SELECT TOP 5 * FROM erp.cliente")

            result = conn.execute(query)

            rows = result.fetchall()

            logging.info(rows)

    except Exception as e:
        logging.error(f"Erro ao ler erp.cliente: {str(e)}")
        raise