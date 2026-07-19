# Asistente Inteligente RAG - Consultorio Médico "Jesús tu Sanador" 🩺

Este proyecto es la solución completa y profesional para el desafío del programa **ONE AI For Tech de Alura Latam**. Consiste en un Agente de Inteligencia Artificial basado en la arquitectura **RAG (Retrieval-Augmented Generation)**, desarrollado con **Python**, **LangChain**, **Streamlit** y **Google Gemini**. El asistente permite a los administradores y personal médico realizar consultas en lenguaje natural sobre la documentación del consultorio, garantizando que el agente responda *únicamente* con la información provista en los archivos cargados.

---

## 🚀 Características Clave

* **Carga de Documentos en Tiempo de Ejecución**: Permite subir múltiples archivos de forma simultánea. Soporta formatos estándar: **PDF**, **DOCX**, **TXT**, y formatos estructurados: **CSV**, **XLSX** (Excel).
* **Ingesta Inteligente de Datos Tabulares (Valor Agregado)**: Los archivos CSV y XLSX se procesan fila por fila, transformando cada registro en textos descriptivos para conservar el contexto relacional en las búsquedas vectoriales.
* **Caché Local de Embeddings (Valor Agregado)**: Implementa `CacheBackedEmbeddings` y `LocalFileStore` en disco para evitar re-calcular embeddings para textos procesados previamente, optimizando el consumo de tokens y acelerando el tiempo de procesamiento.
* **Resiliencia de Cuota y Control de Flujo (Valor Agregado)**: Implementa llamadas por lotes optimizados de 100 fragmentos con tiempos de espera preventivos y reintentos con backoff exponencial. Esto permite indexar documentos de gran tamaño sin saturar los límites de cuota (429 Rate Limits) de las cuentas gratuitas de Gemini.
* **Estricta Restricción de Conocimiento**: El agente responde únicamente en base a los documentos cargados. Si no encuentra la respuesta, contesta exactamente la frase de control obligatoria: *"No encontré esa información dentro de la documentación disponible."*
* **Estética Premium**: Diseño visual moderno, responsivo y adaptado para entornos profesionales del sector de salud, con tipografías personalizadas (`Outfit`), tarjetas informativas, transiciones fluidas y una experiencia limpia.

---

## 🛠️ Arquitectura y Tecnologías

El sistema sigue los principios del patrón RAG moderno estructurado en las siguientes capas:

```text
Usuario (Pregunta) 
    │
    ▼
Streamlit App (Interfaz) ──► Historial de Chat (Session State)
    │
    ▼
Búsqueda Semántica ──► FAISS Vector DB (Almacenamiento Local)
    │
    ▼
Contexto relevante + Pregunta
    │
    ▼
LLM Google Gemini (gemini-flash-latest, Temp=0.0)
    │
    ▼
Respuesta Directa (Estricto apego al contexto)
```

### Tecnologías Principales:
* **Streamlit**: Framework para el desarrollo de la interfaz de usuario web interactiva.
* **LangChain & LangChain Community**: Framework de orquestación para pipelines de IA Generativa.
* **Google Gemini (API)**: Modelos de lenguaje (`gemini-flash-latest`) y de embeddings (`models/gemini-embedding-001`).
* **FAISS (CPU)**: Base de datos vectorial eficiente de Facebook para búsquedas de similitud densa.
* **Pandas & OpenPyXL**: Procesamiento avanzado de archivos tabulares (CSV y Excel).
* **PyPDF & Python-Docx**: Extracción limpia de texto en documentos PDF y Word.

---

## 📂 Estructura del Proyecto

```text
alura_proyecto_consultorio/
│
├── app.py                  # Archivo de entrada principal de Streamlit
├── requirements.txt        # Librerías y dependencias del proyecto
├── README.md               # Este archivo de documentación
├── .gitignore              # Archivos excluidos de control de versiones
├── .env.example            # Ejemplo para variables de entorno locales
│
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuración del proyecto, variables de entorno y constantes
│   ├── ingestion.py        # Lectores de PDF, DOCX, TXT, CSV, XLSX y splitter de texto
│   ├── embeddings.py       # Inicializador de embeddings con caché local y reintentos resilientes
│   ├── vector_db.py        # Control del índice FAISS (crear, guardar, cargar, actualizar)
│   ├── retriever.py        # Lógica de recuperación y búsquedas de similitud
│   ├── prompt.py           # Prompt del sistema para QA restringido
│   ├── agent.py            # Agente RAG principal (cadenas LCEL de LangChain)
│   ├── chat.py             # Gestión del historial y st.session_state
│   └── utils.py            # Utilidades generales (limpieza de archivos, tamaños, formatos)
│
├── data/
│   ├── uploads/            # Directorio temporal para los archivos del usuario (Git ignored)
│   └── vectorstore/        # Almacenamiento local del índice FAISS y caché (Git ignored)
│
└── assets/                 # Recursos gráficos estáticos o capturas (opcional)
```

---

## 💻 Configuración e Instalación Local

Sigue los siguientes pasos para ejecutar el proyecto en tu máquina local:

### 1. Clonar el repositorio
```bash
git clone https://github.com/dieeegovas25/asistente-medico-rag.git
cd asistente-medico-rag
```

### 2. Crear y activar el entorno virtual
En Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
En Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar las dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno
Copia el archivo de ejemplo `.env.example` a un nuevo archivo llamado `.env`:
```bash
cp .env.example .env
```
Abre el archivo `.env` en tu editor de código e introduce tu API Key de Google Gemini:
```env
GOOGLE_API_KEY=AIzaSy...tu_clave_real_de_gemini...
```
*(Puedes obtener una clave de API gratuita en [Google AI Studio](https://aistudio.google.com/))*.

### 5. Ejecutar la aplicación localmente
```bash
streamlit run app.py
```
La aplicación se abrirá automáticamente en tu navegador web en la dirección `http://localhost:8501`.

---

## ☁️ Despliegue en Streamlit Community Cloud

La aplicación está lista para ejecutarse directamente en la nube de Streamlit:

1. Inicia sesión en [Streamlit Share](https://share.streamlit.io/) vinculando tu cuenta de GitHub.
2. Haz clic en **"Create app"** (o **"New app"**).
3. Selecciona tu repositorio (`dieeegovas25/asistente-medico-rag`), la rama (`main`) y el archivo de entrada (`app.py`).
4. Haz clic en **"Advanced settings..."**.
5. En la sección **"Secrets"**, introduce tu API Key de Gemini:
   ```toml
   GOOGLE_API_KEY = "tu_clave_real_de_gemini_aqui"
   ```
6. Haz clic en **"Save"** y luego en **"Deploy!"**.

*   **Enlace Público de la Aplicación Desplegada:** [https://asistente-medico-rag.streamlit.app](https://asistente-medico-rag.streamlit.app)
*   **Repositorio Público:** [https://github.com/dieeegovas25/asistente-medico-rag](https://github.com/dieeegovas25/asistente-medico-rag)

---

## 💬 Ejemplos de Preguntas y Respuestas

Para demostrar el comportamiento restringido y preciso del agente, a continuación se presentan ejemplos reales de interacción con documentos del consultorio:

### Ejemplo 1: Consulta sobre Horarios de Atención
*   **Pregunta del usuario:** `¿Cuáles son los horarios de atención de medicina general los sábados?`
*   **Respuesta del agente:** `El área de medicina general atiende los sábados en el horario de 8:00 AM a 1:00 PM. De lunes a viernes el horario es corrido de 7:00 AM a 7:00 PM.`

### Ejemplo 2: Consulta sobre Tarifas de Servicios
*   **Pregunta del usuario:** `¿Cuál es el costo del servicio de odontología para una profilaxis dental?`
*   **Respuesta del agente:** `De acuerdo con la tabla de tarifas vigentes, la profilaxis dental (limpieza) tiene un costo de $30.00 USD en la especialidad de odontología.`

### Ejemplo 3: Pregunta Fuera de la Documentación (Garantía de Restricción)
*   **Pregunta del usuario:** `¿Cuál es la capital de Italia y cómo está el clima hoy?`
*   **Respuesta del agente:** `No encontré esa información dentro de la documentación disponible.`

---

## 🔍 Funcionamiento del Flujo RAG

1. **Subida**: El usuario carga archivos de reglamento o tarifas a través del File Uploader de Streamlit.
2. **Ingesta y Segmentación**: El sistema lee los archivos físicamente, extrae el texto según el formato, limpia dobles espacios y los divide en fragmentos (chunks) de 1000 caracteres con un traslape de 200 caracteres para asegurar la continuidad de la información.
3. **Indexación**: Cada fragmento se convierte en un vector de alta densidad usando `models/gemini-embedding-001` (Gemini). Los vectores se guardan localmente mediante un índice `FAISS` en disco.
4. **Búsqueda Vectorial**: Cuando el usuario hace una pregunta, se genera su embedding y se buscan los 5 fragmentos más similares en la base de datos vectorial local.
5. **Generación**: El sistema une los fragmentos seleccionados junto al prompt del sistema y la pregunta del usuario. Se envía este contexto a `gemini-flash-latest`, el cual genera la respuesta final o devuelve la frase de restricción predefinida si no está en la documentación.
