from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

def get_retriever(vector_store: FAISS, k: int = 5):
    """
    Retorna el retriever de LangChain configurado para el índice FAISS.
    Permite obtener los 'k' fragmentos más similares a la consulta.
    """
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )

def retrieve_relevant_chunks(vector_store: FAISS, query: str, k: int = 5) -> List[Document]:
    """
    Realiza una búsqueda semántica directa y retorna los chunks relevantes.
    Útil para auditoría y visualización de citas de forma manual en la UI.
    """
    try:
        # Búsqueda semántica simple
        return vector_store.similarity_search(query, k=k)
    except Exception as e:
        print(f"Error durante la recuperación semántica: {str(e)}")
        return []
