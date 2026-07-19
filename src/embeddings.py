import time
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_classic.storage import LocalFileStore
from src import config

# Variable global para patrón Singleton
_cached_embeddings_instance = None

class ResilientGoogleEmbeddings(GoogleGenerativeAIEmbeddings):
    """
    Clase contenedora sobre GoogleGenerativeAIEmbeddings que maneja de manera
    resiliente los límites de cuota (Rate Limits / 429 RESOURCE_EXHAUSTED).
    Optimiza el envío usando lotes grandes (para hacer pocas peticiones por minuto)
    y aplica reintentos con backoff exponencial.
    """
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Aumentar el tamaño del lote a 100. Al hacer lotes grandes, hacemos muchísimas menos
        # llamadas individuales (RPM), lo cual evita saturar la cuota de peticiones por minuto de Gemini.
        batch_size = 100
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            retries = 5
            delay = 6  # Espera inicial en caso de error 429
            
            while retries > 0:
                try:
                    # Invocar el método del padre para el lote actual
                    batch_results = super().embed_documents(batch)
                    results.extend(batch_results)
                    # Retardo preventivo corto entre lotes
                    if len(texts) > batch_size:
                        time.sleep(2.0)
                    break
                except Exception as e:
                    err_msg = str(e)
                    # Capturar errores de cuota agotada (429 / RESOURCE_EXHAUSTED)
                    if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                        print(f"[Aviso RAG] Límite de cuota alcanzado. Reintentando lote en {delay} segundos...")
                        time.sleep(delay)
                        retries -= 1
                        delay *= 2  # Backoff exponencial (6s, 12s, 24s, 48s)
                    else:
                        # Si es otro tipo de error, propagarlo de inmediato
                        raise e
            else:
                raise RuntimeError(
                    "Se superaron los reintentos permitidos debido a la saturación de la API de Google Gemini (429). "
                    "Por favor, espera unos segundos e inténtalo de nuevo."
                )
                
        return results

def get_embeddings():
    """
    Inicializa y retorna los embeddings utilizando Google Gemini (gemini-embedding-001)
    con resiliencia a límites de cuota y caché respaldada en disco.
    """
    global _cached_embeddings_instance
    if _cached_embeddings_instance is not None:
        return _cached_embeddings_instance

    api_key = config.get_api_key()
    if not api_key:
        raise ValueError(
            "La clave de API de Google (GOOGLE_API_KEY) no está configurada. "
            "Por favor, configúrala en el archivo .env o en los secretos de la aplicación."
        )

    # 1. Instanciar los embeddings base de Google usando la clase resiliente
    base_embeddings = ResilientGoogleEmbeddings(
        model=config.EMBEDDINGS_MODEL,
        google_api_key=api_key
    )
    
    # 2. Configurar la ruta física de la caché
    cache_dir = config.VECTORSTORE_DIR / "embeddings_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # 3. Crear el almacén local de archivos binarios
    store = LocalFileStore(str(cache_dir))
    
    # 4. Crear embeddings respaldados por caché
    _cached_embeddings_instance = CacheBackedEmbeddings.from_bytes_store(
        underlying_embeddings=base_embeddings,
        document_embedding_cache=store,
        namespace=base_embeddings.model
    )
    
    return _cached_embeddings_instance
