import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message=".*Pydantic V1.*", category=UserWarning)

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent_dgp import crear_agente, consultar



CARPETA_PROYECTO = Path(__file__).resolve().parent
STATIC_DIR = CARPETA_PROYECTO / "static"

app = FastAPI(
    title="Agente DGP - SEP",
    description="Asistente virtual de la Dirección General de Profesiones (SEP)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_agente = None


def _get_agente():
    global _agente
    if _agente is None:
        _agente = crear_agente()
    return _agente


class ConsultaBody(BaseModel):
    pregunta: str


class ConsultaResponse(BaseModel):
    respuesta: str


@app.get("/", response_class=HTMLResponse)
def index():
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend no encontrado")
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))


@app.get("/health")
def health():
    return {"estado": "ok", "servicio": "agente-dgp"}


@app.post("/api/consultar", response_model=ConsultaResponse)
def api_consultar(body: ConsultaBody):
    
    pregunta = (body.pregunta or "").strip()
    if not pregunta:
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía")
    try:
        agente = _get_agente()
        respuesta = consultar(agente, pregunta)
        return ConsultaResponse(respuesta=respuesta)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
