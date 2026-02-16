"""
Agente DGP Optimizado - Solo Gemini
Con caché y sanitización
"""
import os
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message=".*Pydantic V1.*", category=UserWarning)

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


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

# Cargar datos
_datos_dgp_path = _carpeta_proyecto / "datos_dgp.md"
DATOS_DGP_CONTENIDO = ""
if _datos_dgp_path.exists():
    DATOS_DGP_CONTENIDO = _datos_dgp_path.read_text(encoding="utf-8")
else:
    print(f"ADVERTENCIA: No se encontró {_datos_dgp_path}")

SYSTEM_PROMPT_DGP = """Eres el Asistente Virtual de la DGP-SEP México.

REGLAS CRÍTICAS:
- BREVEDAD: Respuestas de máximo 100 palabras. Si necesita más detalle, pregunta.
- NO REPITAS: Si ya dijiste algo, no lo repitas.
- ALCANCE: Solo temas DGP. Para otros: "Solo atiendo temas de DGP-SEP."
- PRECISIÓN: Si no tienes el dato, remite a profesiones.gob.mx

Usa SOLO la información del CONTEXTO proporcionado."""

def crear_agente():
    """
    Crea agente con Groq (gratis y rápido)
    Requiere GROQ_API_KEY en .env
    """
    from langchain_groq import ChatGroq
    
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
    """
    Consulta al agente con optimizaciones
    """
    if historial is None:
        historial = []
    
    # 1. Sanitizar entrada
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
    
    # 4. Construir prompt con contexto
    prompt_completo = f"""
{SYSTEM_PROMPT_DGP}

CONTEXTO OFICIAL DGP:
{DATOS_DGP_CONTENIDO[:2000]}

PREGUNTA DEL USUARIO:
{pregunta_limpia}
"""
    
    # 5. Invocar Gemini (FORMATO CORREGIDO)
    try:
        # Gemini espera un string directo, no un dict
        respuesta = agente.invoke(prompt_completo)
        
        # Extraer contenido
        if hasattr(respuesta, "content"):
            respuesta = respuesta.content
        else:
            respuesta = str(respuesta)
            
    except Exception as e:
        return f"❌ Error al procesar tu pregunta: {str(e)}"
    
    # 6. Limpiar salida
    respuesta_limpia = limpiar_salida(respuesta)
    
    # 7. Guardar en caché
    if usar_cache:
        _cache_global.set(pregunta_limpia, respuesta_limpia)
    
    return respuesta_limpia

def limpiar_cache():
    """Limpia el caché de respuestas"""
    _cache_global.clear()
    print("✓ Caché limpiado")


def estadisticas_cache():
    """Muestra estadísticas del caché"""
    total = len(_cache_global.cache)
    print(f"📊 Entradas en caché: {total}")
    return total


# Mantener compatibilidad
def crear_llm(model: str = "gemini-2.0-flash", temperature: float = 0.2, api_key: str | None = None):
    """Alias para compatibilidad"""
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    if model:
        os.environ["GOOGLE_MODEL"] = model
    return crear_agente()