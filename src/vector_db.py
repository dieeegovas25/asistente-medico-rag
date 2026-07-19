from pathlib import Path
from typing import List, Tuple, Optional
from langchain_community.vectorstores import FAISS
from src import config
from src.embeddings import get_embeddings
from src.ingestion import process_file

def save_vector_store(vector_store: FAISS) -> None:
    """Guarda el índice FAISS en la ruta local configurada."""
    vector_store.save_local(str(config.FAISS_INDEX_PATH))

def load_vector_store() -> Optional[FAISS]:
    """
    Carga el índice FAISS desde el almacenamiento local.
    Retorna None si el índice no existe.
    """
    if not (config.FAISS_INDEX_PATH / "index.faiss").exists():
        return None
    try:
        embeddings = get_embeddings()
        return FAISS.load_local(
            folder_path=str(config.FAISS_INDEX_PATH),
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        print(f"Error al cargar el índice vectorial FAISS: {str(e)}")
        return None

def build_vector_store(file_paths: List[Path]) -> Tuple[Optional[FAISS], int, int]:
    """
    Recibe una lista de rutas de archivos, procesa cada archivo en chunks,
    genera los embeddings e indexa todo en un nuevo objeto FAISS.
    Retorna una tupla (vector_store, num_documentos_procesados, num_chunks_totales).
    """
    if not file_paths:
        return None, 0, 0

    all_chunks = []
    processed_count = 0

    for file_path in file_paths:
        try:
            chunks = process_file(file_path)
            if chunks:
                all_chunks.extend(chunks)
                processed_count += 1
        except Exception as e:
            # Propagar el error o registrarlo para manejo amigable en la UI
            raise ValueError(f"Error procesando {file_path.name}: {str(e)}")

    if not all_chunks:
        return None, 0, 0

    # Obtener el modelo de embeddings (con caché habilitada)
    embeddings = get_embeddings()

    # Construir el índice FAISS
    vector_store = FAISS.from_documents(all_chunks, embeddings)
    
    # Guardar localmente
    save_vector_store(vector_store)

    return vector_store, processed_count, len(all_chunks)

def rebuild_index_from_uploads() -> Tuple[Optional[FAISS], int, int]:
    """
    Escanea la carpeta de cargas (data/uploads/), procesa todos los archivos
    encontrados y reconstruye el índice vectorial FAISS por completo.
    Esto sincroniza el índice si se eliminan o agregan archivos externamente.
    """
    # Escanear la carpeta de cargas buscando formatos permitidos
    allowed_extensions = {'.pdf', '.docx', '.txt', '.csv', '.xlsx', '.xls'}
    file_paths = []
    
    if config.UPLOADS_DIR.exists():
        for item in config.UPLOADS_DIR.iterdir():
            if item.is_file() and item.suffix.lower() in allowed_extensions:
                file_paths.append(item)

    if not file_paths:
        # Si no hay archivos, eliminar el índice guardado si existe
        clear_stored_index()
        return None, 0, 0

    return build_vector_store(file_paths)

def clear_stored_index() -> None:
    """Elimina los archivos del índice FAISS local."""
    for filename in ["index.faiss", "index.pkl"]:
        file_path = config.FAISS_INDEX_PATH / filename
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                print(f"No se pudo eliminar {filename}: {str(e)}")
                
    # Opcionalmente limpiar también la caché de embeddings si se desea resetear todo
    # En este caso, conservamos la caché de embeddings para optimizar cargas futuras.
