import re
import difflib
from utils import limpiar_palabra

def tokenizar_texto(texto_transcrito, vocabulario, max_sugerencias=3):
    """
    Tokeniza un texto transcrito en lexemas (palabras) limpias y compara cada token
    con el vocabulario. Si el token no está en el vocabulario, se imprime una sugerencia
    basada en distancia de edición.

    Args:
        texto_transcrito (str): Conversación completa (agente + cliente).
        vocabulario (set[str]): Conjunto de palabras válidas en español (sin acentos, todo minúscula).
        max_sugerencias (int): Máximo número de sugerencias a mostrar para tokens desconocidos.

    Returns:
        List[str]: Lista de tokens “limpios” (aunque algunos puedan no estar en vocabulario).
    """
    # Extraer cadenas de caracteres que sean letras y guiones (para no separar "atención-al-cliente", por ejemplo).
    # Luego limpiar con limpiar_palabra para quitar acentos, pasar a minúsculas y eliminar caracteres no alfanuméricos.
    raw_tokens = re.findall(r"[A-Za-zÁÉÍÓÚáéíóúÑñüÜ]+(?:-[A-Za-zÁÉÍÓÚáéíóúÑñüÜ]+)*", texto_transcrito)
    tokens_limpios = []

    for tok in raw_tokens:
        tok_clean = limpiar_palabra(tok)  # Quita acentos y convierte a minúsculas
        if not tok_clean:
            continue
        tokens_limpios.append(tok_clean)

        if tok_clean not in vocabulario:
            # Buscar hasta max_sugerencias coincidencias cercanas en el vocabulario
            sugerencias = difflib.get_close_matches(tok_clean, vocabulario, n=max_sugerencias, cutoff=0.75)
            print(f"Token desconocido: '{tok_clean}'")
            if sugerencias:
                print(f"  Sugerencias: {', '.join(sugerencias)}")
            else:
                print("  No se encontraron sugerencias cercanas.")

    return tokens_limpios


