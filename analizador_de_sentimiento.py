from typing import List, Dict

def analizar_sentimiento(tokens: List[str], lexicon_sentimientos: Dict[str, int]) -> Dict[str, object]:
    """
    Dada una lista de tokens normalizados y un lexicón de sentimientos (palabra->peso),
    calcula:
      - puntaje_total (suma de peso por palabra encontrada en lexicón)
      - count_positivas, count_negativas
      - palabra_mas_positiva (máximo peso), peso
      - palabra_mas_negativa (mínimo peso), peso
      - tokens_no_lexico: lista de tokens que no se encontraron en el lexicón
    Retorna un diccionario con estos campos:
      {
        "sentimiento_general": str,
        "puntaje_total": int,
        "count_positivas": int,
        "palabra_mas_positiva": (str, int),
        "count_negativas": int,
        "palabra_mas_negativa": (str, int),
        "tokens_no_lexico": List[str]
      }
    """
    puntaje_total       = 0
    count_positivas     = 0
    count_negativas     = 0
    max_pos_word        = None
    max_pos_weight      = 0
    max_neg_word        = None
    max_neg_weight      = 0
    tokens_no_lexico    = []

    for tok in tokens:
        peso = lexicon_sentimientos.get(tok)
        if peso is None:
            tokens_no_lexico.append(tok)
            continue

        puntaje_total += peso

        if peso > 0:
            count_positivas += 1
            if peso > max_pos_weight:
                max_pos_weight = peso
                max_pos_word   = tok
        elif peso < 0:
            count_negativas += 1
            if (max_neg_weight == 0) or (peso < max_neg_weight):
                max_neg_weight = peso
                max_neg_word   = tok

    if puntaje_total > 0:
        sentimiento_general = f"Positivo (+{puntaje_total})"
    elif puntaje_total < 0:
        sentimiento_general = f"Negativo ({puntaje_total})"
    else:
        sentimiento_general = "Neutral (0)"

    return {
        "sentimiento_general":   sentimiento_general,
        "puntaje_total":         puntaje_total,
        "count_positivas":       count_positivas,
        "palabra_mas_positiva":  (max_pos_word, max_pos_weight) if max_pos_word else (None, 0),
        "count_negativas":       count_negativas,
        "palabra_mas_negativa":  (max_neg_word, max_neg_weight) if max_neg_word else (None, 0),
        "tokens_no_lexico":      tokens_no_lexico
    }
