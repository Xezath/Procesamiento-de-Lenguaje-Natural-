import re
    
def limpiar_palabra(palabra):
    """Elimina puntuación común al final de una palabra y la convierte a minúsculas."""
    palabra_limpia = re.sub(r'^[^\w]+|[^\w]+$', '', palabra)
    return palabra_limpia.lower()
