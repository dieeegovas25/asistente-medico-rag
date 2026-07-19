import streamlit as st
from typing import List, Dict, Any
from src import config
from src.vector_db import clear_stored_index
from src.utils import clear_uploads_directory

def init_session_state() -> None:
    """
    Inicializa todas las variables de estado necesarias para el chat,
    estadísticas y preguntas sugeridas en st.session_state.
    """
    # Historial de conversación
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Estadísticas del vector store
    if "num_documents" not in st.session_state:
        st.session_state.num_documents = 0
        
    if "num_chunks" not in st.session_state:
        st.session_state.num_chunks = 0
        
    # Preguntas sugeridas dinámicas
    if "suggested_questions" not in st.session_state:
        st.session_state.suggested_questions = []
        
    # Estado del vector store cargado en memoria
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None

    # Pregunta enviada desde un botón sugerido
    if "selected_suggested_question" not in st.session_state:
        st.session_state.selected_suggested_question = None

def add_user_message(content: str) -> None:
    """Agrega un mensaje enviado por el usuario al historial de chat."""
    init_session_state()
    st.session_state.messages.append({
        "role": "user",
        "content": content
    })

def add_assistant_message(content: str, sources: List[Any] = None) -> None:
    """Agrega un mensaje de respuesta del asistente con sus respectivas fuentes."""
    init_session_state()
    st.session_state.messages.append({
        "role": "assistant",
        "content": content,
        "sources": sources or []
    })

def clear_chat_history() -> None:
    """Borra únicamente los mensajes del chat, manteniendo el índice vectorial intacto."""
    st.session_state.messages = []

def reset_all() -> None:
    """
    Reinicia por completo la aplicación:
    - Borra todos los mensajes.
    - Elimina físicamente todos los archivos subidos.
    - Destruye el índice vectorial FAISS guardado localmente.
    - Limpia los estados en memoria de Streamlit.
    """
    # 1. Borrar archivos temporales de uploads
    clear_uploads_directory()
    
    # 2. Borrar base de datos vectorial local
    clear_stored_index()
    
    # 3. Limpiar variables de sesión de Streamlit
    st.session_state.messages = []
    st.session_state.num_documents = 0
    st.session_state.num_chunks = 0
    st.session_state.suggested_questions = []
    st.session_state.vector_store = None
    st.session_state.selected_suggested_question = None
