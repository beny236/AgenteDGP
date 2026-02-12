# Agente DGP - Dirección General de Profesiones (SEP)

Agente de IA para atender al ciudadano y a la sociedad **únicamente** en temas de la **Dirección General de Profesiones (DGP)** de la Secretaría de Educación Pública (SEP): cédulas profesionales, regulación de profesiones, trámites DGP, revalidación, etc.

Desarrollado con **LangChain**, **LangSmith** (trazabilidad) y **Google Gemini 2.5 Flash** como LLM.

## Requisitos

- Python 3.10+
- Cuenta en [Google AI Studio](https://aistudio.google.com/apikey) para `GOOGLE_API_KEY`
- (Opcional) Cuenta en [LangSmith](https://smith.langchain.com/) para trazabilidad

## Instalación

```powershell
cd agent_dgp_v1
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuración

1. Copia el archivo de ejemplo y edita con tus claves:

```bash
copy .env.example .env
```

2. En `.env` define al menos:

- **GOOGLE_API_KEY**: clave de API de Google (obligatoria). Obtén una en https://aistudio.google.com/apikey
- **LANGCHAIN_TRACING_V2**: `true` si quieres ver las trazas en LangSmith.
- **LANGCHAIN_API_KEY**: clave de LangSmith (solo si usas trazabilidad).
- **LANGCHAIN_PROJECT**: nombre del proyecto en LangSmith (ej. `agente-dgp-sep`).

## Uso

**Modo interactivo** (consola):

```bash
python main.py
```

**Una sola pregunta** desde la línea de comandos:

```bash
python main.py ¿Cómo obtengo mi cédula profesional?
```

**Frontend web** (chat en el navegador):

Asegúrate de tener todas las dependencias instaladas (incluida `langchain-google-genai`):

```bash
pip install -r requirements.txt
```

Luego inicia el servidor:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Abre en el navegador: **http://localhost:8000**

## Comportamiento del agente

- Responde **solo** sobre temas de la DGP/SEP: profesiones reguladas, cédulas, trámites, revalidación, Ley del Artículo 5º en materia de profesiones, etc.
- Si la pregunta es sobre otro tema, indica de forma amable que solo atiende temas DGP y sugiere contactar al organismo correspondiente.
- No inventa trámites ni requisitos; en caso de duda sugiere consultar la página oficial de la DGP/SEP.

## Estructura del proyecto

- `agent_dgp.py`: definición del agente (LLM Gemini 2.5 Flash, prompt DGP, cadena LangChain).
- `main.py`: entrada para uso por consola (interactivo o una pregunta).
- `api.py`: API FastAPI que sirve el frontend y el endpoint `/api/consultar`.
- `static/index.html`: frontend básico (chat) para atender al ciudadano desde el navegador.
- `requirements.txt`: dependencias (LangChain, FastAPI, uvicorn, python-dotenv, etc.).
- `.env.example`: plantilla de variables de entorno.

## Licencia

Uso interno / institucional según normativa de la SEP.
