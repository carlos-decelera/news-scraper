import os
import json
import sqlalchemy
from sqlalchemy import create_engine
from google.cloud.sql.connector import Connector, IPTypes
from google.oauth2 import service_account

def get_db_connection():
    """Establece una conexión segura con Google Cloud SQL sin usar variables de entorno del sistema."""
    
    # 1. CARGA DE VARIABLES
    env_creds = os.getenv("GOOGLE_CREDENTIALS")
    instance_name = os.getenv("INSTANCE_CONNECTION_NAME")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_name = os.getenv("DB_NAME")

    if not env_creds:
        raise ValueError("Error: La variable GOOGLE_CREDENTIALS no está configurada en Railway.")

    # 2. PROCESAMIENTO MANUAL DE CREDENCIALES
    # Esto evita que el Connector busque el archivo ADC en el disco
    creds_dict = json.loads(env_creds)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    
    # 3. CONFIGURACIÓN DEL CONECTOR
    # Pasamos las credenciales directamente al constructor aquí
    connector = Connector(credentials=credentials)

    def getconn():
        # Aquí ya no hace falta pasarlas de nuevo, el conector ya las tiene
        conn = connector.connect(
            instance_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=IPTypes.PUBLIC
        )
        return conn

    # 4. CREACIÓN DEL MOTOR (ENGINE)
    engine = create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        echo=False
    )
    
    return engine

# Inicializamos el motor
engine = get_db_connection()

def save_funding_data(data):
    """Inserta datos en la base de datos y retorna True si el registro es nuevo."""
    is_new = False
    
    with engine.connect() as conn:
        # Iniciamos una transacción
        with conn.begin():
            query = sqlalchemy.text("""
                INSERT INTO funding_rounds (company_name, amount, currency, round_type, source_url)
                VALUES (:company_name, :amount, :currency, :round_type, :source_url)
                ON CONFLICT (source_url) DO NOTHING
            """)
            
            result = conn.execute(query, {
                "company_name": data.get('company_name'),
                "amount": data.get('amount'),
                "currency": data.get('currency'),
                "round_type": data.get('round_type'),
                "source_url": data.get('source_url')
            })
            
            if result.rowcount > 0:
                is_new = True
                
    return is_new