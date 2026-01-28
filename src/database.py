import psycopg2
import os

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

def save_funding_data(data):
    conn = get_db_connection()
    is_new = False
    try:
        with conn.cursor() as cur:
            # El "ON CONFLICT DO NOTHING" es clave para no repetir
            query = """
            INSERT INTO funding_rounds (company_name, amount, currency, round_type, source_url)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (source_url) DO NOTHING;
            """
            cur.execute(query, (
                data.get('company_name'),
                data.get('amount'),
                data.get('currency'),
                data.get('round_type'),
                data.get('source_url')
            ))
            if cur.rowcount > 0:
                is_new = True
            conn.commit()
    finally:
        conn.close()
    return is_new