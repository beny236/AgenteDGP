import html
import re
from typing import Optional


def sanitizar_entrada(pregunta: str, max_length: int = 500) -> str:
    """
    Limpia y sanitiza la entrada del usuario
    
    Args:
        pregunta: Pregunta del usuario
        max_length: Longitud máxima permitida
    
    Returns:
        Pregunta sanitizada
    """
    if not pregunta:
        return ""
    
    # 1. Limitar longitud
    pregunta = pregunta[:max_length]
    
    # 2. Escapar HTML (protección XSS)
    pregunta = html.escape(pregunta)
    
    # 3. Remover scripts maliciosos
    pregunta = re.sub(r"<script[^>]*>.*?</script>", "", pregunta, flags=re.IGNORECASE)
    
    # 4. Normalizar espacios
    pregunta = " ".join(pregunta.split())
    
    # 5. Quitar caracteres de control
    pregunta = "".join(c for c in pregunta if c.isprintable() or c == "\n")
    
    return pregunta.strip()


def validar_entrada(pregunta: str) -> tuple[bool, Optional[str]]:
    """
    Valida que la pregunta sea correcta
    
    Returns:
        (es_valida, mensaje_error)
    """
    if not pregunta or len(pregunta.strip()) < 3:
        return False, "La pregunta debe tener al menos 3 caracteres"
    
    if len(pregunta) > 500:
        return False, "La pregunta es demasiado larga (máx 500 caracteres)"
    
    # Detectar spam (demasiada repetición)
    palabras = pregunta.lower().split()
    if len(palabras) > 0 and len(set(palabras)) < len(palabras) * 0.3:
        return False, "La pregunta contiene demasiada repetición"
    
    return True, None


def limpiar_salida(texto: str) -> str:
    """
    Limpia la respuesta del modelo
    
    Args:
        texto: Respuesta del LLM
        
    Returns:
        Respuesta limpia
    """
    if not texto:
        return ""
    
    # Limpiar espacios múltiples
    texto = re.sub(r" +", " ", texto)
    
    # Limpiar líneas vacías múltiples
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    
    # Limpiar al inicio/final
    texto = texto.strip()
    
    # Asegurar puntuación final
    if texto and texto[-1] not in ".!?":
        texto += "."
    
    return texto