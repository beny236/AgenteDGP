"""
Script principal para uso por consola del Agente DGP Optimizado
"""
import sys
from pathlib import Path
from agent_dgp import crear_agente, consultar, limpiar_cache, estadisticas_cache

CARPETA_PROYECTO = Path(__file__).resolve().parent


def main():
    print("="*60)
    print("Cargando Agente DGP Optimizado...")
    print("="*60)
    
    try:
        agente = crear_agente()
        print("✓ Agente cargado correctamente")
        print("✓ Sistema de caché inicializado")
        print("✓ RAG se inicializará en la primera consulta")
    except ValueError as e:
        print(f"\n❌ Error de configuración: {e}")
        print("\n📋 Pasos para configurar:")
        print("1. Asegúrate de tener un archivo .env")
        print("2. Agrega tu GROQ_API_KEY al .env")
        print("3. Ejecuta nuevamente: python main.py\n")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("¡Hola! 👋 Soy el asistente de la DGP-SEP.")
    print("Puedo ayudarte con trámites, cédulas y temas afines.")
    print("="*60)
    
    print("\n💡 Comandos especiales:")
    print("  - 'salir' o 'quit': Terminar")
    print("  - 'limpiar': Limpiar caché")
    print("  - 'stats': Ver estadísticas\n")
    
    # Modo de pregunta única
    if len(sys.argv) > 1:
        pregunta = " ".join(sys.argv[1:])
        print(f"Usuario: {pregunta}")
        respuesta = consultar(agente, pregunta)
        print(f"\nDGP: {respuesta}\n")
        return
    
    # Modo interactivo
    while True:
        try:
            pregunta = input("\n🙋 Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 ¡Hasta luego!")
            break
        
        if not pregunta:
            continue
        
        pregunta_lower = pregunta.lower()
        
        # Comandos especiales
        if pregunta_lower in ("salir", "quit", "exit"):
            print("\n👋 ¡Hasta luego!")
            break
        
        if pregunta_lower == "limpiar":
            limpiar_cache()
            continue
        
        if pregunta_lower == "stats":
            estadisticas_cache()
            continue
        
        # Procesar pregunta
        respuesta = consultar(agente, pregunta)
        print(f"\n🤖 DGP: {respuesta}")


if __name__ == "__main__":
    main()