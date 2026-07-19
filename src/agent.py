import re
from typing import List, Dict, Any, Tuple, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from src import config, prompt

class RAGAgent:
    """
    Agente RAG principal para el Consultorio Médico 'Jesús tu Sanador'.
    Se encarga de formular respuestas restrictivas basadas únicamente en
    el vector store y de generar preguntas de sugerencia de manera dinámica.
    """
    def __init__(self, vector_store: Optional[FAISS] = None):
        # Inicializar el LLM de Google con temperatura 0 para respuestas precisas y deterministas
        self.llm = ChatGoogleGenerativeAI(
            model=config.LLM_MODEL,
            google_api_key=config.get_api_key(),
            temperature=0.0
        )
        self.vector_store = vector_store
        self.qa_prompt = PromptTemplate.from_template(prompt.SYSTEM_QA_PROMPT)

    def set_vector_store(self, vector_store: FAISS) -> None:
        """Actualiza el vector store utilizado por el agente."""
        self.vector_store = vector_store

    def answer(self, question: str) -> Dict[str, Any]:
        """
        Responde a la pregunta del usuario usando búsqueda semántica y el LLM.
        Garantiza apego estricto al contexto proporcionado.
        """
        if not self.vector_store:
            return {
                "answer": "No encontré esa información dentro de la documentación disponible.",
                "sources": []
            }

        # 1. Recuperar los fragmentos más relevantes del vector store (k=5)
        from src.retriever import retrieve_relevant_chunks
        docs = retrieve_relevant_chunks(self.vector_store, question, k=5)

        if not docs:
            return {
                "answer": "No encontré esa información dentro de la documentación disponible.",
                "sources": []
            }

        # 2. Formatear el contexto indicando explícitamente el origen de cada fragmento
        context_text = ""
        for doc in docs:
            src = doc.metadata.get("source", "Documento")
            # Agregar información detallada si es PDF (páginas) o Excel (hoja y fila)
            if "page" in doc.metadata:
                src_details = f"{src} (Pág. {doc.metadata['page']})"
            elif "sheet" in doc.metadata:
                src_details = f"{src} (Hoja: {doc.metadata['sheet']}, Fila: {doc.metadata['row']})"
            elif "row" in doc.metadata:
                src_details = f"{src} (Fila: {doc.metadata['row']})"
            else:
                src_details = src

            context_text += f"--- FUENTE: {src_details} ---\n{doc.page_content}\n\n"

        # 3. Construir la cadena de ejecución LCEL
        chain = self.qa_prompt | self.llm | StrOutputParser()

        try:
            # Ejecutar el modelo
            answer_text = chain.invoke({
                "context": context_text,
                "question": question
            })
            
            # Post-procesamiento opcional para asegurar limpieza
            cleaned_answer = answer_text.strip()
            
            return {
                "answer": cleaned_answer,
                "sources": docs
            }
        except Exception as e:
            return {
                "answer": f"Ocurrió un error al procesar tu consulta con el modelo de lenguaje: {str(e)}",
                "sources": []
            }

    def generate_suggested_questions(self, max_chunks: int = 8) -> List[str]:
        """
        Genera dinámicamente entre 5 y 10 preguntas sugeridas a partir del
        contenido indexado en el vector store.
        Para optimizar tokens, extrae una muestra balanceada de chunks de
        las diferentes fuentes sin volver a leer los archivos.
        """
        if not self.vector_store:
            return []

        # 1. Extraer los documentos de la memoria interna de FAISS
        try:
            doc_dict = self.vector_store.docstore._dict
            all_docs = list(doc_dict.values())
        except Exception as e:
            print(f"Error al acceder al docstore de FAISS: {str(e)}")
            return self._fallback_questions()

        if not all_docs:
            return []

        # 2. Agrupar por fuente para asegurar que las preguntas sugeridas cubran varios documentos
        docs_by_source = {}
        for doc in all_docs:
            src = doc.metadata.get("source", "Documento")
            if src not in docs_by_source:
                docs_by_source[src] = []
            docs_by_source[src].append(doc)

        # 3. Selección equitativa de chunks de cada archivo
        selected_docs = []
        if len(all_docs) <= max_chunks:
            selected_docs = all_docs
        else:
            sources = list(docs_by_source.keys())
            idx = 0
            # Ciclar sobre las fuentes agregando el primer chunk disponible de cada una
            while len(selected_docs) < max_chunks and any(len(docs_by_source[s]) > 0 for s in sources):
                current_source = sources[idx % len(sources)]
                if docs_by_source[current_source]:
                    selected_docs.append(docs_by_source[current_source].pop(0))
                idx += 1

        # 4. Formatear el contexto representativo
        representative_context = ""
        for doc in selected_docs:
            src = doc.metadata.get("source", "Archivo")
            representative_context += f"[Archivo: {src}]\n{doc.page_content}\n\n"

        # 5. Invocar al modelo para la creación de preguntas
        suggested_prompt = PromptTemplate.from_template(prompt.SUGGESTED_QUESTIONS_PROMPT)
        chain = suggested_prompt | self.llm | StrOutputParser()

        try:
            response = chain.invoke({"context": representative_context})
            
            # Limpiar y separar por líneas
            questions = []
            for line in response.split("\n"):
                line = line.strip()
                if not line:
                    continue
                # Limpiar cualquier viñeta, numeración o guión al inicio
                cleaned_q = re.sub(r'^[-*#\s\d\.]+', '', line).strip()
                if cleaned_q:
                    # Garantizar formato de pregunta
                    if not cleaned_q.startswith("¿"):
                        cleaned_q = "¿" + cleaned_q
                    if not cleaned_q.endswith("?"):
                        cleaned_q = cleaned_q + "?"
                    questions.append(cleaned_q)

            # Devolver entre 5 y 10 preguntas válidas y únicas
            unique_questions = list(dict.fromkeys(questions))  # Preserva el orden eliminando duplicados
            final_questions = [q for q in unique_questions if len(q) > 12]
            
            if len(final_questions) < 5:
                # Si falló la generación de suficientes preguntas, rellenar con fallbacks
                fallbacks = self._fallback_questions()
                for fb in fallbacks:
                    if fb not in final_questions:
                        final_questions.append(fb)
                    if len(final_questions) >= 7:
                        break
                        
            return final_questions[:10]  # Cap máximo de 10
        except Exception as e:
            print(f"Error generando preguntas sugeridas con Gemini: {str(e)}")
            return self._fallback_questions()

    def _fallback_questions(self) -> List[str]:
        """Preguntas genéricas de respaldo en caso de error."""
        return [
            "¿Cuáles son los horarios de atención del consultorio?",
            "¿Qué especialidades médicas y servicios se ofrecen?",
            "¿Cuáles son las tarifas generales y formas de pago?",
            "¿Cómo se programan, reprograman o cancelan las citas?",
            "¿Cuáles son los protocolos internos de higiene y atención?"
        ]
