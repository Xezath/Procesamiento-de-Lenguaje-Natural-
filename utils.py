import re
from unidecode import unidecode

def limpiar_palabra(palabra: str) -> str:
    """
    Elimina puntuación al inicio y final de la palabra, convierte a minúsculas,
    quita tildes/acentos y filtra caracteres no alfanuméricos.
    Ej: "ÓSCAR." -> "oscar"
    """
    # 1. Quitar puntuación al inicio/final
    palabra_limpia = re.sub(r'^[^\w]+|[^\w]+$', '', palabra)
    # 2. Convertir a minúsculas y quitar tildes/acentos
    palabra_limpia = unidecode(palabra_limpia.lower())
    # 3. Eliminar cualquier carácter que no sea letra o número
    palabra_limpia = re.sub(r'[^a-z0-9ñ]', '', palabra_limpia)
    return palabra_limpia
