# Asistente Inteligente RAG - Consultorio Médico "Jesús tu Sanador" 🩺

Este proyecto es la solución completa y profesional para el desafío del programa **ONE AI For Tech de Alura Latam**. Consiste en un Agente de Inteligencia Artificial basado en la arquitectura **RAG (Retrieval-Augmented Generation)**, desarrollado con **Python**, **LangChain**, **Streamlit** y **Google Gemini**. El asistente permite a los administradores y personal médico realizar consultas en lenguaje natural sobre la documentación del consultorio, garantizando que el agente responda *únicamente* con la información provista en los archivos cargados.

---

## 🚀 Características Clave

* **Carga de Documentos en Tiempo de Ejecución**: Permite subir múltiples archivos de forma simultánea. Soporta formatos estándar: **PDF**, **DOCX**, **TXT**, y formatos estructurados: **CSV**, **XLSX** (Excel).
* **Ingesta Inteligente de Datos Tabulares (Valor Agregado)**: Los archivos CSV y XLSX se procesan fila por fila, transformando cada registro en textos descriptivos para conservar el contexto relacional en las búsquedas vectoriales.
* **Caché Local de Embeddings (Valor Agregado)**: Implementa `CacheBackedEmbeddings` y `LocalFileStore` en disco para evitar re-calcular embeddings para textos procesados previamente, optimizando el consumo de tokens y acelerando el tiempo de procesamiento.
* **Generación Dinámica de Preguntas Sugeridas**: Cuando se indexan documentos, el modelo LLM analiza de forma inteligente y dinámica una muestra del contenido del vectorstore y genera entre 5 y 10 preguntas sugeridas en la interfaz de usuario. Al hacer clic en ellas, se consultan inmediatamente.
* **Citas Detalladas y Auditoría (Valor Agregado)**: Cada respuesta incluye un bloque expandible que muestra las fuentes exactas consultadas (nombre de archivo, página, hoja de cálculo, fila y fragmento de texto original).
* **Estricta Restricción de Conocimiento**: El agente responde únicamente en base a los documentos cargados. Si no encuentra la respuesta, contesta exactamente: *"No encontré esa información dentro de la documentación disponible."*
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
LLM Google Gemini (gemini-1.5-flash, Temp=0.0)
    │
    ▼
Respuesta + Citas del origen del documento
```

### Tecnologías Principales:
* **Streamlit**: Framework para el desarrollo de la interfaz de usuario web interactiva.
* **LangChain & LangChain Community**: Framework de orquestación para pipelines de IA Generativa.
* **Google Gemini (API)**: Modelos de lenguaje (`gemini-1.5-flash`) y de embeddings (`text-embedding-004`).
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
│   ├── embeddings.py       # Inicializador de embeddings con caché local en disco
│   ├── vector_db.py        # Control del índice FAISS (crear, guardar, cargar, actualizar)
│   ├── retriever.py        # Lógica de recuperación y búsquedas de similitud
│   ├── prompt.py           # Prompts del sistema para QA y preguntas sugeridas
│   ├── agent.py            # Agente RAG principal (cadenas LCEL de LangChain)
│   ├── chat.py             # Gestión del historial y st.session_state
│   └── utils.py            # Utilidades generales (limpieza de archivos, tamaños, formatos)
│
├── data/
│   ├── uploads/            # Directorio temporal para los archivos del usuario (Git ignored)
│   └── vectorstore/        # Almacenamiento local del índice FAISS y caché (Git ignored)
│
└── assets/                 # Recursos gráficos estáticos (opcional)
```

---

## 💻 Configuración e Instalación Local

Sigue los siguientes pasos para ejecutar el proyecto en tu máquina local:

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/consultorio-ai.git
cd consultorio-ai
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

Para desplegar la aplicación de forma gratuita en la nube de Streamlit, sigue estos pasos:

### 1. Subir el proyecto a GitHub
Crea un nuevo repositorio en GitHub (asegúrate de que el archivo `.env` **no** esté incluido; para eso sirve el `.gitignore`) y sube tu código:
```bash
git init
git add .
git commit -m "Initial commit: RAG Agent Jesús tu Sanador"
git branch -M main
git remote add origin https://github.com/tu-usuario/consultorio-ai.git
git push -u origin main
```

### 2. Crear la aplicación en Streamlit Cloud
1. Inicia sesión en [Streamlit Share](https://share.streamlit.io/) con tu cuenta de GitHub.
2. Haz clic en el botón **"Create app"** (o **"New app"**).
3. Selecciona tu repositorio (`tu-usuario/consultorio-ai`), la rama (`main`) y el archivo de entrada (`app.py`).

### 3. Configurar los Secrets
Antes de hacer clic en Deploy, debes configurar tu API Key en la plataforma para que el código la pueda leer de forma segura:
1. En la pantalla de creación, haz clic en **"Advanced settings..."**.
2. En la sección **"Secrets"**, introduce tu API Key en formato TOML:
   ```toml
   GOOGLE_API_KEY = "tu_clave_real_de_gemini_aqui"
   ```
3. Haz clic en **"Save"**.
4. Finalmente, haz clic en **"Deploy!"**. Streamlit instalará las dependencias de `requirements.txt` automáticamente y tu aplicación estará en línea en pocos minutos.

---

## 🔍 Funcionamiento del Flujo RAG

1. **Subida**: El usuario carga archivos de reglamento o tarifas a través del File Uploader de Streamlit.
2. **Ingesta y Segmentación**: El sistema lee los archivos físicamente, extrae el texto según el formato, limpia dobles espacios y los divide en fragmentos (chunks) de 1000 caracteres con un traslape de 200 caracteres para asegurar la continuidad de la información.
3. **Indexación**: Cada fragmento se convierte en un vector de alta densidad usando `text-embedding-004` (Gemini). Los vectores se guardan localmente mediante un índice `FAISS` en disco.
4. **Búsqueda Vectorial**: Cuando el usuario hace una pregunta, se genera su embedding y se buscan los 5 fragmentos más similares en la base de datos vectorial local.
5. **Generación**: El sistema une los fragmentos seleccionados junto al prompt del sistema y la pregunta del usuario. Se envía este contexto a `gemini-1.5-flash`, el cual genera la respuesta final o devuelve la frase de restricción predefinida si no está en la documentación.
6. **Despliegue**: Las citas se listan al final de la respuesta mostrando el origen exacto del archivo utilizado para responder.
