import re
import difflib
from typing import List, Dict, Tuple
from utils import limpiar_palabra

def tokenizar_texto(
    texto_transcrito: str,
    vocabulario: set,
    max_sugerencias: int = 3,
    cutoff: float = 0.75,
    interactivo: bool = False
) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Tokeniza el texto en lexemas normalizados (sin tildes, minúsculas).
    Omite tokens que sean únicamente números.
    Para cada token que no esté en 'vocabulario', sugiere correcciones basadas en difflib.
    Si 'interactivo' es True, pregunta al usuario si desea agregar tokens desconocidos.

    Retorna:
      tokens_limpios: List[str]
      sugerencias: Dict[token_invalido, List[str]]
    """
    # Extraer secuencias de letras y dígitos
    raw_tokens = re.findall(r"[A-Za-zÑñÁÉÍÓÚáéíóú0-9]+", texto_transcrito)
    tokens_limpios: List[str] = []
    sugerencias: Dict[str, List[str]] = {}

    for tok in raw_tokens:
        # Omitir tokens que sean sólo números:
        if tok.isdigit():
            continue

        tok_clean = limpiar_palabra(tok)
        if not tok_clean:
            continue

        tokens_limpios.append(tok_clean)

        if tok_clean not in vocabulario:
            # Generar sugerencias
            matches = difflib.get_close_matches(tok_clean, vocabulario, n=max_sugerencias, cutoff=cutoff)
            sugerencias[tok_clean] = matches

            if interactivo:
                print(f"\nToken desconocido: '{tok_clean}'")
                if matches:
                    print(f"  Sugerencias: {matches}")
                else:
                    print("  Sin sugerencias cercanas.")
                resp = input("¿Agregar este token al vocabulario? [s/N]: ").strip().lower()
                if resp == 's':
                    voto = input("¿Cuál es la puntuación de sentimiento para esta palabra? [−3…+3]: ").strip()
                    try:
                        peso = int(voto)
                        # Devolver al llamador la nueva palabra y su peso para que la guarde en CSV
                        sugerencias[tok_clean].append(f"AGREGAR_COMO({peso})")
                    except ValueError:
                        print("  Puntuación inválida. Se omite agregar.")
    return tokens_limpios, sugerencias