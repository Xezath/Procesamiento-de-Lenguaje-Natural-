import re
import difflib
import csv
import os
from typing import List, Dict, Tuple
from utils import limpiar_palabra

# Lista fija de categorías pragmáticas
CATEGORIAS = ["saludo", "despedida", "identificacion", "palabra_ruda", "otros"]

def cargar_vocabulario(path_csv: str) -> Dict[str, Tuple[str,int]]:
    """
    Carga el CSV de vocabulario pragmático con columnas:
      palabra,categoria,puntaje
    Retorna un dict: { palabra: (categoria, puntaje) }.
    """
    vocab = {}
    if not os.path.isfile(path_csv):
        return vocab

    with open(path_csv, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            palabra = row[0].strip().lower()
            categoria = row[1].strip()
            try:
                puntaje = int(row[2])
            except ValueError:
                continue
            vocab[palabra] = (categoria, puntaje)
    return vocab

def tokenizar_texto(
    texto_transcrito: str,
    vocabulario: Dict[str, Tuple[str,int]],
    max_sugerencias: int = 3,
    cutoff: float = 0.75,
    interactivo: bool = False
) -> Tuple[List[Tuple[str,str,int]], Dict[str, List[str]]]:
    """
    Tokeniza el texto en lexemas normalizados (sin tildes, minúsculas).
    Omite tokens que sean únicamente números.
    Para cada token:
      - Si existe en 'vocabulario', extrae (categoria, puntaje).
      - Si no existe, genera sugerencias ortográficas (difflib).
        Si 'interactivo' es True, pregunta:
          1. ¿Desea reemplazar por alguna sugerencia?
          2. Si no, ¿Agregar como nuevo token con categoría pragmática?
    Retorna:
      tokens_info: List[ (token, categoria, puntaje) ]
      sugerencias: Dict[token_invalido, List[sugerencias_ortográficas>]
    """
    raw_tokens = re.findall(r"[A-Za-zÑñÁÉÍÓÚáéíóú0-9]+", texto_transcrito)
    tokens_info: List[Tuple[str,str,int]] = []
    sugerencias: Dict[str, List[str]] = {}

    for tok in raw_tokens:
        # Omitir secuencias puramente numéricas
        if tok.isdigit():
            continue

        tok_clean = limpiar_palabra(tok)
        if not tok_clean:
            continue

        # Si el token ya existe en el vocabulario, anexamos directo
        if tok_clean in vocabulario:
            categoria, puntaje = vocabulario[tok_clean]
            tokens_info.append((tok_clean, categoria, puntaje))
            continue

        # Generar sugerencias ortográficas
        matches = difflib.get_close_matches(
            tok_clean, vocabulario.keys(),
            n=max_sugerencias, cutoff=cutoff
        )
        sugerencias[tok_clean] = matches

        if not interactivo:
            # Modo no interactivo: categorizar como "otros"
            tokens_info.append((tok_clean, "otros", 0))
            continue

        # -----------------------
        # MODO INTERACTIVO AQUI
        # -----------------------
        print(f"\nToken desconocido: '{tok_clean}'")
        if matches:
            print("  Sugerencias cercanas:")
            for idx, sugerencia in enumerate(matches):
                print(f"    [{idx}] {sugerencia}")
            print("    [n] Ninguna de las anteriores")
            sel = input("  ¿Reemplazar por alguna sugerencia? (índice o 'n'): ").strip().lower()
            if sel.isdigit():
                i = int(sel)
                if 0 <= i < len(matches):
                    reemplazo = matches[i]
                    cat_rep, peso_rep = vocabulario[reemplazo]
                    print(f"  → Usando sugerencia: '{reemplazo}' "
                          f"(categoría='{cat_rep}', puntaje={peso_rep})")
                    tokens_info.append((reemplazo, cat_rep, peso_rep))
                    continue
                else:
                    print("  Índice fuera de rango. Se omite reemplazo.")
            else:
                print("  No se usará ninguna sugerencia para este token.")
        else:
            print("  Sin sugerencias cercanas.")

        # Mostrar lista numerada de categorías pragmáticas
        print("\n  Escoja categoría pragmática para este token:")
        for idx, cat in enumerate(CATEGORIAS):
            print(f"    [{idx}] {cat}")
        sel_cat = input("  Ingrese el número de la categoría (o Enter para 'otros'): ").strip()

        if sel_cat.isdigit() and 0 <= int(sel_cat) < len(CATEGORIAS):
            categoria_elegida = CATEGORIAS[int(sel_cat)]
        else:
            categoria_elegida = "otros"

        # Preguntar puntaje de sentimiento
        voto = input("  Puntaje de sentimiento para este token (−3…+3, defecto=0): ").strip()
        try:
            puntaje = int(voto)
        except ValueError:
            puntaje = 0

        # Guardar en memoria y en CSV si la categoría no es 'otros'
        vocabulario[tok_clean] = (categoria_elegida, puntaje)
        with open("vocabulario_sentimiento.csv", "a", encoding="utf-8", newline="") as fcsv:
            writer = csv.writer(fcsv)
            writer.writerow([tok_clean, categoria_elegida, str(puntaje)])

        tokens_info.append((tok_clean, categoria_elegida, puntaje))

    return tokens_info, sugerencias
