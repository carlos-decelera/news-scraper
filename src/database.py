import os
import json
from google.cloud.sql.connector import Connector
import psycopg2

def get_db_connection():
    # 1. Cargamos el JSON desde la variable de entorno
    creds_info = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
    
    # 2. Inicializamos el conector de Google Cloud SQL
    # Esto elimina la necesidad de abrir IPs o usar SSL manual
    connector = Connector(credentials_info=creds_info)

    def getconn():
        conn = connector.connect(
            os.getenv("INSTANCE_CONNECTION_NAME"), # Ej: "proyecto:region:instancia"
            "pg8000",
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("DB_NAME")
        )
        return conn

    # 3. Retornamos la conexión (usando pg8000 que es más compatible con el conector)
    return getconn()