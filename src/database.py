import os
import json
import sqlalchemy
from sqlalchemy import create_engine
from google.cloud.sql.connector import Connector, IPTypes
from google.oauth2 import service_account

def get_db_connection():
    # 1. CARGA Y VALIDACIÓN DE VARIABLES
    env_creds = os.getenv("GOOGLE_CREDENTIALS")
    instance_name = os.getenv("INSTANCE_CONNECTION_NAME")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_name = os.getenv("DB_NAME")

    # Validación crítica para evitar el error de 'NoneType'
    if not all([env_creds, instance_name, db_user, db_pass, db_name]):
        raise ValueError("Error: Faltan variables de entorno (DB_PASS, INSTANCE_NAME, etc.) en Railway.")

    creds_dict = json.loads(env_creds)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    
    # Usamos el conector como un objeto global para gestionar el pool correctamente
    connector = Connector(credentials=credentials)

    def getconn():
        return connector.connect(
            instance_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=IPTypes.PUBLIC
        )

    # El engine debe crearse fuera de la función de inserción para reutilizar conexiones
    return create_engine("postgresql+pg8000://", creator=getconn, echo=False)

# Inicializamos el motor una sola vez
engine = get_db_connection()

def save_funding_data(data):
    """Inserta o actualiza datos. Retorna True si es un registro nuevo."""
    is_new = False
    
    with engine.connect() as conn:
        with conn.begin():
            # Usamos ON CONFLICT para actualizar si ya existe (Upsert)
            # o simplemente DO NOTHING si solo queremos detectar nuevos
            query = sqlalchemy.text("""
                INSERT INTO funding_rounds (company_name, amount, currency, round_type, source_url)
                VALUES (:company_name, :amount, :currency, :round_type, :source_url)
                ON CONFLICT (source_url) 
                DO UPDATE SET 
                    company_name = EXCLUDED.company_name,
                    amount = EXCLUDED.amount,
                    currency = EXCLUDED.currency,
                    round_type = EXCLUDED.round_type
                WHERE EXCLUDED.company_name != 'N/A'
            """)
            
            result = conn.execute(query, {
                "company_name": data.get('company_name', 'N/A'),
                "amount": data.get('amount'),
                "currency": data.get('currency'),
                "round_type": data.get('round_type'),
                "source_url": data.get('source_url')
            })
            
            # Si se insertó una fila nueva o se actualizó una existente
            if result.rowcount > 0:
                is_new = True
                
    return is_new

def check_if_url_exists(url):
    """Verifica si una URL ya está en la base de datos."""
    with engine.connect() as conn:
        query = sqlalchemy.text("SELECT 1 FROM funding_rounds WHERE source_url = :url LIMIT 1")
        result = conn.execute(query, {"url": url})
        return result.fetchone() is not None

def save_empty_article(url):
    """Guarda una URL con datos vacíos para marcarla como 'procesada'."""
    with engine.connect() as conn:
        with conn.begin():
            query = sqlalchemy.text("""
                INSERT INTO funding_rounds (source_url, company_name) 
                VALUES (:url, 'N/A') 
                ON CONFLICT (source_url) DO NOTHING
            """)
            conn.execute(query, {"url": url})