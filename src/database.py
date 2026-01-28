import os
import json
import sqlalchemy
from sqlalchemy import create_engine
from google.cloud.sql.connector import Connector, IPTypes
from google.oauth2 import service_account

def get_db_connection():
    """Establece una conexión segura con Google Cloud SQL usando el conector oficial."""
    
    # 1. CARGA DE VARIABLES DE ENTORNO
    # En Railway, pega el contenido del JSON en esta variable
    env_creds = os.getenv("GOOGLE_CREDENTIALS")
    instance_name = os.getenv("INSTANCE_CONNECTION_NAME")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_name = os.getenv("DB_NAME")

    if not env_creds:
        raise ValueError("Error: La variable GOOGLE_CREDENTIALS no está configurada en Railway.")

    # 2. PROCESAMIENTO DE CREDENCIALES
    # Convertimos el string JSON en un objeto de credenciales de Google
    creds_dict = json.loads(env_creds)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    
    # 3. CONFIGURACIÓN DEL CONECTOR
    connector = Connector()

    def getconn():
        """Función interna que el motor de SQLAlchemy llamará para abrir conexiones."""
        conn = connector.connect(
            instance_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=IPTypes.PUBLIC,
            credentials=credentials
        )
        return conn

    # 4. CREACIÓN DEL MOTOR (ENGINE)
    # Usamos pg8000 como driver para PostgreSQL
    engine = create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        echo=False # Cambia a True si quieres ver las consultas SQL en los logs
    )
    
    return engine

# Inicializamos el motor globalmente para que main.py pueda usarlo
engine = get_db_connection()

def save_funding_data(data):
    """
    Inserta datos en la base de datos. 
    Retorna True si el registro es nuevo (no duplicado).
    """
    is_new = False
    
    # Abrimos una conexión del pool
    with engine.connect() as conn:
        with conn.begin():
            # El ON CONFLICT (source_url) DO NOTHING evita procesar noticias repetidas
            # Asegúrate de que tu tabla 'funding_rounds' tenga source_url como UNIQUE
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
            
            # Si se insertó una fila, es un registro nuevo
            if result.rowcount > 0:
                is_new = True
                
    return is_new