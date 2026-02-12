import sys
from pathlib import Path

from agent_dgp import crear_agente, consultar

CARPETA_PROYECTO = Path(__file__).resolve().parent


def main():
    print("Cargando Agente DGP (Dirección General de Profesiones - SEP)...")
    try:
        agente = crear_agente()
    except ValueError as e:
        env_path = CARPETA_PROYECTO / ".env"
        env_example = CARPETA_PROYECTO / ".env.example"
        if not env_path.exists() and env_example.exists():
            env_path.write_text(env_example.read_text(encoding="utf-8"), encoding="utf-8")
            print("Se creó el archivo .env en la carpeta del proyecto.")
        print(f"Error de configuración: {e}")
        print("Abre el archivo .env y asigna tu clave en GOOGLE_API_KEY (obtén una en https://aistudio.google.com/apikey).")
        print("Luego ejecuta de nuevo: python main.py")
        sys.exit(1)

    print("Listo. Solo respondo temas relacionados al módulo de profesionistas en México).")
    print("Escribe 'salir' o 'quit' para terminar.\n")

    if len(sys.argv) > 1:
        pregunta = " ".join(sys.argv[1:])
        respuesta = consultar(agente, pregunta)
        print(f"Ciudadano: {pregunta}\nDGP: {respuesta}")
        return


    while True:
        try:
            pregunta = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            break
        if not pregunta:
            continue
        if pregunta.lower() in ("salir", "quit", "exit"):
            print("Hasta luego.")
            break
        respuesta = consultar(agente, pregunta)
        print(f"DGP: {respuesta}\n")


if __name__ == "__main__":
    main()
