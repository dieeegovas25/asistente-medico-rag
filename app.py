import streamlit as st
from pathlib import Path
from src import config, chat, utils
from src.agent import RAGAgent
from src.vector_db import load_vector_store, rebuild_index_from_uploads

# 1. Configurar la página de Streamlit
st.set_page_config(
    page_title="Consultorio Jesús tu Sanador - Asistente RAG",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inyectar estilos CSS para una estética Premium (Tema Médico)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Configuración de tipografía global */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Encabezado principal estilizado */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0E5E6F;
        text-align: center;
        margin-bottom: 5px;
    }
    .main-subtitle {
        font-size: 1.2rem;
        color: #3A8891;
        text-align: center;
        margin-bottom: 25px;
        font-weight: 400;
    }
    
    /* Diseño premium de tarjetas para el sidebar y detalles */
    .sidebar-card {
        background-color: #F2F9F9;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #3A8891;
        margin-bottom: 15px;
    }
    
    /* Botones de preguntas sugeridas interactivos */
    .stButton>button {
        border-radius: 8px;
        border: 1px solid #3A8891;
        background-color: #FFFFFF;
        color: #0E5E6F;
        font-weight: 500;
        transition: all 0.3s ease;
        padding: 8px 15px;
        text-align: left;
    }
    
    .stButton>button:hover {
        background-color: #3A8891;
        color: #FFFFFF;
        border-color: #3A8891;
        box-shadow: 0 4px 6px rgba(58, 136, 145, 0.2);
        transform: translateY(-1px);
    }
    
    /* Fuentes y citas expanders */
    .source-block {
        background-color: #F8FAFC;
        border-left: 3px solid #64748B;
        padding: 8px 12px;
        margin-top: 5px;
        margin-bottom: 10px;
        border-radius: 4px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# 3. Inicializar el estado de la sesión de Streamlit
chat.init_session_state()

# 4. Intentar cargar el índice vectorial existente si no está cargado en memoria
if st.session_state.vector_store is None:
    existing_store = load_vector_store()
    if existing_store:
        st.session_state.vector_store = existing_store
        # Extraer estadísticas del docstore de FAISS
        try:
            doc_dict = existing_store.docstore._dict
            chunks = list(doc_dict.values())
            unique_sources = set(doc.metadata.get("source") for doc in chunks if "source" in doc.metadata)
            st.session_state.num_documents = len(unique_sources)
            st.session_state.num_chunks = len(chunks)
        except Exception:
            st.session_state.num_documents = 0
            st.session_state.num_chunks = 0
        


# 5. Crear el Sidebar
with st.sidebar:
    st.markdown("<div style='text-align: center; margin-bottom: 15px;'>", unsafe_allow_html=True)
    st.markdown("## 🩺 Jesús tu Sanador")
    st.markdown("Asistente Virtual RAG")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Descripción del Proyecto
    st.markdown("<div class='sidebar-card'>", unsafe_allow_html=True)
    st.markdown("**Sobre el Asistente:**")
    st.markdown(
        "Este agente inteligente utiliza la arquitectura **RAG (Generación Aumentada por Recuperación)** "
        "para responder dudas sobre tarifas, horarios, especialidades y reglamentos del consultorio. "
        "Sus respuestas están limitadas *únicamente* a los documentos que tú proporciones."
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Estadísticas del Índice
    st.markdown("### 📊 Estadísticas de Documentos")
    st.metric(label="Documentos Cargados", value=st.session_state.num_documents)
    st.metric(label="Chunks (Fragmentos) Creados", value=st.session_state.num_chunks)
    
    st.divider()
    
    # Tecnologías Utilizadas
    st.markdown("**Tecnologías Utilizadas:**")
    st.caption("• Streamlit (Interfaz Web)")
    st.caption("• LangChain (Pipeline RAG)")
    st.caption("• Google Gemini (LLM & Embeddings)")
    st.caption("• FAISS (Índice Vectorial Local)")
    st.caption("• Python (Ingesta de archivos)")
    
    st.divider()
    
    # Acciones de Control
    st.markdown("### 🛠️ Acciones de Control")
    
    col_side1, col_side2 = st.columns(2)
    with col_side1:
        if st.button("🔄 Reconstruir Índice", use_container_width=True, help="Vuelve a leer la carpeta temporal de subidas y reconstruye el índice FAISS"):
            if not config.is_api_key_configured():
                st.error("API Key no configurada.")
            else:
                with st.spinner("Reconstruyendo..."):
                    vector_store, num_docs, num_chunks = rebuild_index_from_uploads()
                    st.session_state.vector_store = vector_store
                    st.session_state.num_documents = num_docs
                    st.session_state.num_chunks = num_chunks

                st.success("Índice reconstruido.")
                st.rerun()
                
    with col_side2:
        if st.button("🧹 Limpiar Chat", use_container_width=True, help="Limpia la conversación actual del historial"):
            chat.clear_chat_history()
            st.rerun()
            
    if st.button("🚨 Reiniciar Sesión Completa", use_container_width=True, type="primary", help="Borra archivos, índice y chat de forma permanente"):
        chat.reset_all()
        st.success("Sesión reiniciada con éxito.")
        st.rerun()

# 6. Área Principal
st.markdown("<h1 class='main-title'>Consultorio Médico \"Jesús tu Sanador\"</h1>", unsafe_allow_html=True)
st.markdown("<p class='main-subtitle'>Asistente Inteligente con IA para Consultas Internas de Documentación</p>", unsafe_allow_html=True)

# Validación de API Key de Google
if not config.is_api_key_configured():
    st.warning("⚠️ **Clave de API de Google Gemini (GOOGLE_API_KEY) no configurada**")
    st.info(
        "Para ejecutar la aplicación localmente, copia el archivo `.env.example` a `.env` e ingresa tu API Key "
        "de Google. Si estás en Streamlit Community Cloud, agrégala en la pestaña **Secrets** de los ajustes de tu aplicación."
    )

# File Uploader en la zona principal
st.markdown("### 📥 1. Carga de Documentos del Consultorio")
uploaded_files = st.file_uploader(
    "Carga uno o más documentos (formatos soportados: PDF, DOCX, TXT, CSV, XLSX)",
    type=["pdf", "docx", "txt", "csv", "xlsx", "xls"],
    accept_multiple_files=True,
    help="Al cargar archivos, el índice vectorial se creará y actualizará automáticamente para su consulta inmediata."
)

# Guardar archivos subidos y reconstruir índice si hay diferencias
if uploaded_files:
    # Retorna True si los archivos difieren de los actualmente almacenados
    with st.spinner("Guardando y verificando archivos..."):
        file_change_detected = False
        
        # Comprobar tamaños y nombres para ver si cambiaron
        existing_names = {f.name for f in config.UPLOADS_DIR.iterdir() if f.is_file() and f.name != ".gitkeep"}
        uploaded_names = {f.name for f in uploaded_files}
        
        if existing_names != uploaded_names:
            file_change_detected = True
            
        if not file_change_detected:
            # Si los nombres son iguales, comparar tamaños
            for uploaded_file in uploaded_files:
                target_path = config.UPLOADS_DIR / uploaded_file.name
                if not target_path.exists() or target_path.stat().st_size != uploaded_file.size:
                    file_change_detected = True
                    break
                    
        if file_change_detected:
            # Guardar físicamente los archivos
            utils.clear_uploads_directory()
            for uploaded_file in uploaded_files:
                file_path = config.UPLOADS_DIR / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                    
            # Reconstruir índice
            if config.is_api_key_configured():
                with st.spinner("Procesando documentos y actualizando índice vectorial..."):
                    vector_store, num_docs, num_chunks = rebuild_index_from_uploads()
                    st.session_state.vector_store = vector_store
                    st.session_state.num_documents = num_docs
                    st.session_state.num_chunks = num_chunks
                    

                st.success("¡Documentos cargados e indexados exitosamente!")
                st.rerun()
else:
    # Si el usuario removió los archivos desde el componente, limpiar el directorio
    existing_files_count = len([f for f in config.UPLOADS_DIR.iterdir() if f.is_file() and f.name != ".gitkeep"])
    if existing_files_count > 0:
        utils.clear_uploads_directory()
        chat.reset_all()
        st.info("Todos los documentos han sido eliminados. El índice y el chat se han reiniciado.")
        st.rerun()

# 7. Sección de Consultas y Chat
st.markdown("### 💬 2. Área de Consultas")



# Inicializar variable para capturar la consulta del usuario
user_query = None

# Recibir entrada desde el campo de chat tradicional
chat_input = st.chat_input("Escribe tu pregunta sobre la documentación del consultorio...")

# Determinar si la entrada provino del chat input o de las preguntas sugeridas
if chat_input:
    user_query = chat_input

# Procesar la consulta del usuario si se ha enviado alguna
if user_query:
    if not config.is_api_key_configured():
        st.error("No se puede consultar el asistente virtual porque la clave de API (GOOGLE_API_KEY) no está configurada.")
    elif st.session_state.vector_store is None:
        st.warning("Por favor, carga al menos un documento antes de consultar al asistente.")
    else:
        # Registrar pregunta del usuario en el historial
        chat.add_user_message(user_query)
        
        # Ejecutar la inferencia del agente RAG
        with st.spinner("Analizando documentos y generando respuesta..."):
            agent = RAGAgent(st.session_state.vector_store)
            response = agent.answer(user_query)
            
            # Registrar la respuesta del asistente en el historial
            chat.add_assistant_message(response["answer"], response["sources"])
            
        st.rerun()

# 8. Renderizar el historial de conversación en el Chat
if st.session_state.messages:
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            

else:
    # Mensaje de bienvenida inicial en el chat si no hay historial
    with st.chat_message("assistant"):
        st.markdown(
            "¡Hola! Soy el Asistente Virtual del **Consultorio Médico \"Jesús tu Sanador\"**.\n\n"
            "Por favor, carga uno o más documentos (PDF, DOCX, TXT, CSV o Excel) para comenzar. "
            "Una vez cargados, analizaré la información y podré responder todas tus preguntas basándome "
            "exclusivamente en esos archivos. ¡Estaré atento a tus indicaciones!"
        )
