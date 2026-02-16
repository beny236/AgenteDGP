import os
from pathlib import Path
from typing import List

# Importar con manejo de errores
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
except ImportError:
    print("⚠️ Instalando dependencias de RAG...")
    os.system("pip install -q chromadb sentence-transformers langchain-community")
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document


class RAGSystem:
    """Sistema RAG simplificado para DGP"""
    
    def __init__(self, carpeta_docs: Path):
        self.carpeta_docs = carpeta_docs
        self.vectorstore = None
        self.embeddings = None
        print("🔄 Inicializando sistema RAG...")
        self._inicializar()
    
    def _inicializar(self):
        """Crea o carga el índice vectorial"""
        persist_dir = Path("./chroma_db")
        
        # Si ya existe, cargar
        if persist_dir.exists():
            print("📂 Cargando vectorstore existente...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            self.vectorstore = Chroma(
                persist_directory=str(persist_dir),
                embedding_function=self.embeddings
            )
            print("✓ Vectorstore cargado")
        else:
            print("🆕 Creando nuevo vectorstore (esto tarda ~30 segundos la primera vez)...")
            self._crear_vectorstore()
    
    def _crear_vectorstore(self):
        """Crea el vectorstore desde cero"""
        # 1. Cargar documentos .md
        print("📄 Cargando documentos...")
        documentos = []
        for archivo_md in self.carpeta_docs.glob("*.md"):
            contenido = archivo_md.read_text(encoding="utf-8")
            documentos.append(
                Document(
                    page_content=contenido,
                    metadata={"source": archivo_md.name}
                )
            )
        
        if not documentos:
            raise ValueError(f"No se encontraron archivos .md en {self.carpeta_docs}")
        
        print(f"✓ {len(documentos)} documentos cargados")
        
        # 2. Dividir en chunks
        print("✂️ Dividiendo en chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n## ", "\n### ", "\n- ", "\n", " "]
        )
        chunks = text_splitter.split_documents(documentos)
        print(f"✓ {len(chunks)} chunks creados")
        
        # 3. Crear embeddings
        print("🧠 Creando embeddings...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 4. Crear vectorstore
        print("💾 Guardando vectorstore...")
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )
        print("✅ RAG inicializado correctamente")
    
    def buscar_contexto(self, pregunta: str, k: int = 2) -> str:
        """
        Busca los chunks más relevantes
        
        Args:
            pregunta: Pregunta del usuario
            k: Número de chunks a recuperar
            
        Returns:
            Contexto relevante concatenado
        """
        if not self.vectorstore:
            return ""
        
        # Búsqueda semántica
        docs = self.vectorstore.similarity_search(pregunta, k=k)
        
        # Formatear contexto
        partes = []
        for doc in docs:
            fuente = doc.metadata.get("source", "")
            partes.append(f"[Fuente: {fuente}]\n{doc.page_content}")
        
        contexto = "\n\n---\n\n".join(partes)
        
        print(f"🔍 Recuperados {len(docs)} chunks relevantes")
        return contexto


# Singleton global
_rag_instance = None

def get_rag_system(carpeta_docs: Path = None) -> RAGSystem:
    """Obtiene instancia singleton del RAG"""
    global _rag_instance
    if _rag_instance is None:
        if carpeta_docs is None:
            carpeta_docs = Path(__file__).parent
        _rag_instance = RAGSystem(carpeta_docs)
    return _rag_instance