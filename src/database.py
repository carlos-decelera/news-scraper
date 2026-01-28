import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector, IPTypes

# --- 1. CARGA DE VARIABLES ---
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")
# Railway: Asegúrate de que la variable se llame exactamente GOOGLE_CREDENTIALS
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS")

# --- 2. LÓGICA DE CONEXIÓN SEGURA (OPTIMIZADA) ---
if GOOGLE_CREDENTIALS_JSON:
    print("🔒 Conectando a Google Cloud SQL vía Connector (In-Memory)...")
    
    # Parseamos el JSON para pasarlo directamente
    creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
    
    # Inicializamos el conector con las credenciales cargadas
    connector = Connector(credentials_info=creds_dict)

    def getconn():
        conn = connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pg8000",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
            ip_type=IPTypes.PUBLIC
        )
        return conn

    engine = create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
else:
    print("⚠️ Usando Fallback Local (SQLite)...")
    engine = create_engine("sqlite:///./test.db")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# A partir de aquí tus modelos (Company, Dealflow) siguen exactamente igual