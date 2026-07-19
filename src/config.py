import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env si existe
load_dotenv()

# Rutas del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"

# Crear directorios necesarios si no existen
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

# Configuraciones de Modelos de Inteligencia Artificial (Google Gemini)
# Modelo de lenguaje para responder y generar preguntas sugeridas
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash")
# Modelo de generación de embeddings
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "models/gemini-embedding-001")

# Configuraciones del Splitter (división del texto)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Ruta para guardar el índice de FAISS local
FAISS_INDEX_PATH = VECTORSTORE_DIR / "faiss_index"

def get_api_key() -> str:
    """
    Obtiene la API Key de Google de las variables de entorno.
    Soporta carga local mediante archivo .env y en la nube de Streamlit.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    return api_key or ""

def is_api_key_configured() -> bool:
    """Verifica si la API Key está configurada."""
    return len(get_api_key()) > 0
