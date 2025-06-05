import os
import csv
from tokenizacion import tokenizar_texto
from analizador_de_sentimiento import analizar_sentimiento
from protocolo import verificar_protocolo

# ------------------------------
# Configuración general
# ------------------------------
VOC_LEX_CSV       = "vocabulario_sentimiento.csv"
TRANSCRIPTION_FILE = "transcripcion.txt"
INTERACTIVO       = False  # Cambiar a True para activar validación interactiva de tokens


def load_vocab_and_lexicon(path: str):
    """
    Carga un CSV con columnas: palabra,activo,ponderacion
    - Si activo == 1, la palabra se agrega al vocabulario.
    - Siempre se registra en lexicon con su ponderación.
    Retorna (vocabulario: set[str], lexicon: dict[str,int]).
    """
    vocab = set()
    lexicon = {}
    if not os.path.isfile(path):
        print(f"[ERROR] No se encontró {path}")
        return vocab, lexicon

    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            palabra = row[0].strip()
            try:
                activo = int(row[1])
                peso   = int(row[2])
            except ValueError:
                continue

            # Normalizamos la palabra a minúsculas (ya debe venir limpia en el CSV)
            clave = palabra.lower()
            lexicon[clave] = peso
            if activo == 1:
                vocab.add(clave)

    return vocab, lexicon


def append_to_lexicon_csv(path: str, palabra: str, peso: int):
    """
    Agrega una nueva fila al CSV de vocabulario y sentimientos:
      palabra,1,peso
    """
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([palabra, "1", str(peso)])


def generar_reporte(sentiment_report: dict, protocolo_report: dict, sugerencias: dict):
    """
    Imprime por consola el reporte final combinando:
      - Tokens desconocidos y sus sugerencias.
      - Análisis de Sentimiento.
      - Verificación del Protocolo (Agente).
    """
    # 1) Tokens desconocidos y sugerencias
    if sugerencias:
        print("\n--- TOKENS NO RECONOCIDOS ---")
        for tok, opts in sugerencias.items():
            # Filtramos marcadores de "AGREGAR_COMO(...)"
            clean_opts = [o for o in opts if not isinstance(o, str) or not o.startswith("AGREGAR_COMO(")]
            if clean_opts:
                print(f"  - '{tok}'  →  Sugerencias: {clean_opts}")
            else:
                print(f"  - '{tok}'  →  (Sin sugerencias)")
    else:
        print("\nTodos los tokens se reconocieron en el vocabulario.")

    # 2) Análisis de Sentimiento
    print("\n--- ANÁLISIS DE SENTIMIENTO ---")
    puntaje       = sentiment_report["puntaje_total"]
    pos_count     = sentiment_report["count_positivas"]
    neg_count     = sentiment_report["count_negativas"]
    pos_word, pw  = sentiment_report["palabra_mas_positiva"]
    neg_word, nw  = sentiment_report["palabra_mas_negativa"]

    if puntaje > 0:
        sentimiento_general = f"Positivo (+{puntaje})"
    elif puntaje < 0:
        sentimiento_general = f"Negativo ({puntaje})"
    else:
        sentimiento_general = "Neutral (0)"

    print(f"Sentimiento general: {sentimiento_general}")
    print(f"Palabras positivas: {pos_count}")
    if pos_word:
        print(f"  → Palabra más positiva: {pos_word}, +{pw}")
    else:
        print("  → Sin palabras positivas.")
    print(f"Palabras negativas: {neg_count}")
    if neg_word:
        print(f"  → Palabra más negativa: {neg_word}, {nw}")
    else:
        print("  → Sin palabras negativas.")

    # 3) Verificación de Protocolo (Agente)
    print("\n--- VERIFICACIÓN DEL PROTOCOLO (Agente) ---")
    saludo_ok = protocolo_report["saludo"]["ok"]
    print(f"Saludo inicial: {'OK' if saludo_ok else 'Faltante'}")

    id_ok = protocolo_report["identificacion"]["ok"]
    print(f"Identificación del cliente: {'OK' if id_ok else 'Faltante'}")

    palabras_rudas = protocolo_report["rudas"]["lista"]
    if palabras_rudas:
        print(f"Uso de palabras rudas: {palabras_rudas}")
    else:
        print("Uso de palabras rudas: Ninguna detectada")

    despedida_ok = protocolo_report["despedida"]["ok"]
    print(f"Despedida amable: {'OK' if despedida_ok else 'Faltante'}")

    print("\n===================== FIN REPORTE =====================\n")


if __name__ == "__main__":
    # 1) Cargar vocabulario y lexicón de sentimiento
    vocabulario, lexicon = load_vocab_and_lexicon(VOC_LEX_CSV)

    # 2) Leer transcripción completa
    if not os.path.isfile(TRANSCRIPTION_FILE):
        print(f"[ERROR] No se encontró {TRANSCRIPTION_FILE}")
        exit(1)

    with open(TRANSCRIPTION_FILE, encoding="utf-8") as f:
        full_transcript = f.read()

    # 3) Separar líneas de Agente y Cliente
    agente_lines  = []
    cliente_lines = []
    for line in full_transcript.splitlines():
        l = line.strip()
        if not l:
            continue
        if l.lower().startswith("agente:"):
            agente_lines.append(l[len("agente:"):].strip())
        elif l.lower().startswith("cliente:"):
            cliente_lines.append(l[len("cliente:"):].strip())
        else:
            # Si no tiene prefijo, se asigna al último hablante según conteo
            if agente_lines and (len(agente_lines) >= len(cliente_lines)):
                agente_lines[-1] += " " + l
            elif cliente_lines:
                cliente_lines[-1] += " " + l

    texto_agente  = " ".join(agente_lines)
    texto_cliente = " ".join(cliente_lines)

    # 4) Tokenizar texto del Agente y Cliente
    tokens_agente,  sugerencias_ag  = tokenizar_texto(texto_agente,  vocabulario, interactivo=INTERACTIVO)
    tokens_cliente, sugerencias_cl  = tokenizar_texto(texto_cliente, vocabulario, interactivo=INTERACTIVO)
    tokens_totales = tokens_agente + tokens_cliente

    # 5) Si está en modo interactivo, procesar marcadores de "AGREGAR_COMO(...)"
    if INTERACTIVO:
        combined_sug = {**sugerencias_ag, **sugerencias_cl}
        for tok, opts in combined_sug.items():
            for opt in opts:
                if isinstance(opt, str) and opt.startswith("AGREGAR_COMO("):
                    # Extraer peso
                    try:
                        peso = int(opt[len("AGREGAR_COMO(") : -1])
                        if tok not in vocabulario:
                            append_to_lexicon_csv(VOC_LEX_CSV, tok, peso)
                            vocabulario.add(tok)
                            lexicon[tok] = peso
                            print(f"→ Se agregó '{tok}' con peso {peso} al lexicón.")
                    except ValueError:
                        pass

    # Unir sugerencias (sin duplicar claves)
    sugerencias = {**sugerencias_ag, **sugerencias_cl}

    # 6) Análisis de Sentimiento (usa tokens normalizados)
    sentiment_report = analizar_sentimiento(tokens_totales, lexicon)

    # 7) Verificación de Protocolo (solo con tokens del Agente y texto del Agente)
    protocolo_report = verificar_protocolo(tokens_agente, texto_agente)

    # 8) Generar y mostrar reporte
    generar_reporte(sentiment_report, protocolo_report, sugerencias)
