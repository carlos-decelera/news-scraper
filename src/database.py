import os
import json
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy

def get_db_connection():
    # Cargamos las credenciales desde la variable de entorno de Railway
    creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
    
    # Inicializamos el conector con las credenciales
    connector = Connector(credentials_info=creds_dict)

    def getconn():
        conn = connector.connect(
            os.getenv("INSTANCE_CONNECTION_NAME"),
            "pg8000",
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("DB_NAME"),
            ip_type=IPTypes.PUBLIC  # Usa la IP pública de tu Cloud SQL
        )
        return conn

    # Creamos un motor de base de datos (Engine) de SQLAlchemy para manejar el pool
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return pool.connect()