import os
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message=".*Pydantic V1.*", category=UserWarning)

from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Importar sistemas
from cache_system import SimpleCache
from sanitization import sanitizar_entrada, validar_entrada, limpiar_salida

# Configuración
_carpeta_proyecto = Path(__file__).resolve().parent
_env_path = _carpeta_proyecto / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
else:
    load_dotenv()

# Caché global
_cache_global = SimpleCache(ttl_seconds=3600)

# System prompt optimizado
SYSTEM_PROMPT_DGP = """Eres un asistente de la DGP-SEP. Tu ÚNICA tarea es encontrar y responder con la información exacta del archivos_md.

INSTRUCCIONES OBLIGATORIAS:
1. Los archivos "datos_dgp.md","profesionista_dgp.md","instituciones_educativas_dgp.md","colegios_federaciones_dgp.md"
    tienen toda la información que necesitas para emitir una respuesta.
2. Cuando encuentres precios (con símbolo $), fechas, o datos específicos - ÚSALOS en tu respuesta
3. Responde en máximo 4 oraciones
EJEMPLO CORRECTO:
Usuario: "¿Cuánto cuesta la cédula?"
CONTEXTO contiene: "Expedición de Cédula para Nivel Licenciatura: $1,840.00"
TU RESPUESTA: "La cédula profesional para nivel licenciatura cuesta $1,840.00"
PROHIBIDO responder "no tengo información" si el CONTEXTO tiene la respuesta.
"""

def cargar_documentos():
    """Carga todos los archivos .md al inicio"""
    archivos_md = [
        "datos_dgp.md",
        "profesionista_dgp.md",
        "instituciones_educativas_dgp.md",
        "colegios_federaciones_dgp.md"
    ]
    
    contenido_total = []
    archivos_cargados = []
    
    for archivo in archivos_md:
        ruta = _carpeta_proyecto / archivo
        if ruta.exists():
            try:
                contenido = ruta.read_text(encoding="utf-8")
                contenido_total.append(f"\n\n--- {archivo} ---\n{contenido}")
                archivos_cargados.append(archivo)
            except Exception as e:
                print(f"⚠️ Error al cargar {archivo}: {e}")
        else:
            print(f"⚠️ No se encontró: {archivo}")
    
    if archivos_cargados:
        print(f"✓ Documentos cargados: {', '.join(archivos_cargados)}")
    else:
        print("❌ ADVERTENCIA: No se cargó ningún documento")
    
    return "\n".join(contenido_total)


def cargar_documentos_relevantes(pregunta: str) -> str:
    """Carga solo documentos relevantes según la pregunta"""
    pregunta_lower = pregunta.lower()
    
    # Siempre cargar datos generales
    docs_a_cargar = ["datos_dgp.md"]
    
    # Detectar área por palabras clave
    if any(palabra in pregunta_lower for palabra in [
        "cédula", "cedula", "profesionista", "título", "titulo", 
        "pasante", "constancia", "tramite", "trámite",
        "cuesta", "costo", "precio", "pago", "cuanto", "cuánto"
    ]):
        docs_a_cargar.append("profesionista_dgp.md")
    
    if any(palabra in pregunta_lower for palabra in [
        "institución", "institucion", "educativa", "universidad", 
        "escuela", "plantel"
    ]):
        docs_a_cargar.append("instituciones_educativas_dgp.md")
    
    if any(palabra in pregunta_lower for palabra in [
        "colegio", "federación", "federacion", "asociación", "asociacion"
    ]):
        docs_a_cargar.append("colegios_federaciones_dgp.md")
    
    # Si no detecta área específica, carga todo
    if len(docs_a_cargar) == 1:
        docs_a_cargar = [
            "datos_dgp.md",
            "profesionista_dgp.md",
            "instituciones_educativas_dgp.md",
            "colegios_federaciones_dgp.md"
        ]
        print("🔍 No se detectó área específica, cargando todos los documentos")
    else:
        print(f"🔍 Área detectada, cargando: {', '.join(docs_a_cargar)}")
    
    # Cargar y retornar
    contenido = []
    for doc in docs_a_cargar:
        ruta = _carpeta_proyecto / doc
        if ruta.exists():
            try:
                texto = ruta.read_text(encoding="utf-8")
                contenido.append(f"\n--- {doc} ---\n{texto}")
            except Exception as e:
                print(f"⚠️ Error al cargar {doc}: {e}")
    
    return "\n\n".join(contenido)


# Cargar todo al inicio
DATOS_DGP_CONTENIDO = cargar_documentos()


def crear_agente():
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    
    if not api_key:
        raise ValueError(
            "❌ Se requiere GROQ_API_KEY en el archivo .env\n"
            "Obtén tu clave GRATIS en: https://console.groq.com/keys"
        )
    
    modelo = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    llm = ChatGroq(
        api_key=api_key,
        model=modelo,
        temperature=0.2,
        max_tokens=300
    )
    
    print(f"✓ Agente Groq creado (modelo: {modelo})")
    return llm


def consultar(agente, pregunta: str, historial: list | None = None, usar_cache: bool = True) -> str:
    if historial is None:
        historial = []
    
    # 1. Sanitizar
    pregunta_limpia = sanitizar_entrada(pregunta)
    
    # 2. Validar
    es_valida, error = validar_entrada(pregunta_limpia)
    if not es_valida:
        return f"❌ {error}"
    
    # 3. Verificar caché
    if usar_cache:
        respuesta_cache = _cache_global.get(pregunta_limpia)
        if respuesta_cache:
            return respuesta_cache
    
    # 4. Obtener documentos relevantes
    contexto_relevante = cargar_documentos_relevantes(pregunta_limpia)
    
    # DEBUG
    print("\n" + "="*60)
    print("🔍 CONTEXTO ENVIADO AL LLM:")
    print(f"Longitud: {len(contexto_relevante)} caracteres")
    print(contexto_relevante)
    print("="*60 + "\n")
    
    # 5. Construir prompt
    prompt_completo = f"""{SYSTEM_PROMPT_DGP}

CONTEXTO OFICIAL DGP:
{contexto_relevante[:9000]}

PREGUNTA DEL USUARIO:
{pregunta_limpia}
"""
    
    # 6. Invocar LLM
    try:
        respuesta = agente.invoke(prompt_completo)
        if hasattr(respuesta, "content"):
            respuesta = respuesta.content
        else:
            respuesta = str(respuesta)
    except Exception as e:
        return f"❌ Error: {str(e)}"
    
    # 7. Limpiar
    respuesta_limpia = limpiar_salida(respuesta)
    
    # 8. Guardar en caché
    if usar_cache:
        _cache_global.set(pregunta_limpia, respuesta_limpia)
    
    return respuesta_limpia


def limpiar_cache():
    """Limpia el caché"""
    _cache_global.clear()
    print("✓ Caché limpiado")


def estadisticas_cache():
    total = len(_cache_global.cache)
    print(f"📊 Entradas en caché: {total}")
    return total


def crear_llm(model: str = "gemini-2.0-flash-exp", temperature: float = 0.2, api_key: str | None = None):
    return crear_agente()