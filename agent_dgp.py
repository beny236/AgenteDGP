import os
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message=".*Pydantic V1.*", category=UserWarning)

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

_carpeta_proyecto = Path(__file__).resolve().parent
_env_path = _carpeta_proyecto / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
else:
    load_dotenv()

# Cargar el archivo de datos oficiales
_datos_dgp_path = _carpeta_proyecto / "datos_dgp.md"
DATOS_DGP_CONTENIDO = ""
if _datos_dgp_path.exists():
    DATOS_DGP_CONTENIDO = _datos_dgp_path.read_text(encoding="utf-8")
else:
    print(f"ADVERTENCIA: No se encontró el archivo {_datos_dgp_path}")


SYSTEM_PROMPT_DGP = """Eres un asistente virtual oficial de la Dirección General de Profesiones (DGP) de la Secretaría de Educación Pública (SEP) de México.

INFORMACIÓN OFICIAL DE LA DGP:
{datos_oficiales}

Tu ÚNICA función es atender consultas de ciudadanos y sociedad sobre:
- Informa que que no contamos con atención presencial para ninún trámite. A partir del 1 de marzo, todos los trámites para Profesionistas (Constancias de No Sanción / Constancias por Título en Trámite / Constancias de Pasante / Expedición de la Cédula profesional / Vinculación de CURP con Cédula profesional) se gestionarán exclusivamente a través de nuestra página web.
- Información actual como el director general, visión, misión, enfoque etc...
- Cédulas profesionales (obtención, verificación)
- Trámites que pueden realizar los profesionistas ante la DGP (Vincular la CURP con la Cédula,Cédula profesionl, Constancias de No Sanción, Constancias por Título en Trámite,Constancias de Pasante)
- Cualquier trámite o información que dependa de la DGP/SEP en materia de profesiones.
- Compartir la información de la DGP/SEP con el ciudadano de manera clara y concisa.
- Explicar el proceso para obtener la cédula.
- Explicar el proceso para realizar el trámite corresppondiente a la constancia de no sanción.
- Explicar el proceso para realizar el trámite corresppondiente a la constancia de Título en trámite.
- Explicar el proceso para realizar el trámite corresppondiente a la constancia de pasante.
- Explicarel proceso de Vinculación de CURP




REGLAS ESTRICTAS:
1. SOLO responde preguntas relacionadas con la DGP y las profesiones reguladas por la SEP.
2. Si te preguntan sobre otro tema (política general, otros organismos, temas personales no relacionados con profesiones), responde de forma amable pero firme: "Soy el asistente de la Dirección General de Profesiones (DGP) de la SEP. Solo puedo ayudarte con trámites, cédulas profesionales, regulación de profesiones y temas afines a la DGP. Para otros temas, te sugiero contactar al organismo correspondiente."
3. Sé claro, preciso y respetuoso. Usa lenguaje ciudadano cuando sea posible.
4. Si no estás seguro de un procedimiento específico, recomienda consultar la página oficial de la DGP/SEP o acudir a ventanilla.
5. No inventes trámites ni requisitos; si no lo sabes, indícalo y sugiere fuentes oficiales.
6. Verifica que la información sea actualizada y vigente basándote en los datos oficiales proporcionados.
7. Usa SIEMPRE la información del archivo de datos oficiales para responder con precisión.
"""


def crear_llm(
    model: str = "gemini-2.5-flash",
    temperature: float = 0.3,
    api_key: str | None = None,
) -> ChatGoogleGenerativeAI:
   
    key = (api_key or os.getenv("GOOGLE_API_KEY") or "").strip()
    if not key or key == "tu_clave_aqui":
        raise ValueError(
            "Se requiere GOOGLE_API_KEY. Definela en el entorno o pásala como argumento. "
            "Obtén tu clave en https://aistudio.google.com/apikey"
        )
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        google_api_key=key,
    )


def crear_agente(llm: ChatGoogleGenerativeAI | None = None):
    if llm is None:
        llm = crear_llm()

    # Insertar los datos oficiales en el prompt del sistema
    prompt_con_datos = SYSTEM_PROMPT_DGP.format(datos_oficiales=DATOS_DGP_CONTENIDO)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_con_datos),
        MessagesPlaceholder(variable_name="historial", optional=True),
        ("human", "{pregunta}"),
    ])

    chain = prompt | llm
    return chain


def consultar(agente, pregunta: str, historial: list | None = None) -> str:
    if historial is None:
        historial = []
    mensaje = agente.invoke({"pregunta": pregunta, "historial": historial})
    return mensaje.content if hasattr(mensaje, "content") else str(mensaje)