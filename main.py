import os
import sys
import csv
from tokenizacion import cargar_vocabulario, tokenizar_texto
from analizador_de_sentimiento import analizar_sentimiento
from protocolo import verificar_protocolo

# ------------------------------
# Configuración general
# ------------------------------
VOC_LEX_CSV        = "vocabulario_sentimiento.csv"
TRANSCRIPTION_FILE = "transcripcion.txt"
INTERACTIVO        = False  # Cambiar a True para validación interactiva de nuevos tokens


def load_lexicon(path: str) -> dict[str,int]:
    """
    Carga un CSV con columnas: palabra,categoria,puntaje
    Devuelve un dict { palabra: puntaje } para análisis de sentimiento.
    """
    lexicon = {}
    if not os.path.isfile(path):
        return lexicon

    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            palabra = row[0].strip().lower()
            try:
                peso = int(row[2])
            except ValueError:
                continue
            lexicon[palabra] = peso
    return lexicon


def generar_reporte(sentiment_report: dict, protocolo_report: dict, sugerencias_ag: dict, sugerencias_cl: dict):
    """
    Imprime por consola el reporte final combinando:
      - Tokens desconocidos y sus sugerencias.
      - Análisis de Sentimiento (total, counts, extremos).
      - Verificación del Protocolo (Agente).
    """
    # 1) Tokens desconocidos (Agente + Cliente)
    sugerencias = {**sugerencias_ag, **sugerencias_cl}
    if sugerencias:
        print("\n--- TOKENS NO RECONOCIDOS ---")
        for tok, opts in sugerencias.items():
            clean_opts = [o for o in opts if not (isinstance(o, str) and o.startswith("AGREGAR_COMO("))]
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

    print(f"Sentimiento general: {sentiment_report['sentimiento_general']}")
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
    # 1) Cargar vocabulario completo (palabra->(categoría,puntaje))
    vocab_catalog = cargar_vocabulario(VOC_LEX_CSV)
    vocabulario = set(vocab_catalog.keys())  # solo llaves para tokenizar
    # 2) Cargar lexicón (palabra->puntaje) para análisis de sentimiento
    lexicon = load_lexicon(VOC_LEX_CSV)

    # 3) Leer transcripción completa
    if not os.path.isfile(TRANSCRIPTION_FILE):
        print(f"[ERROR] No se encontró {TRANSCRIPTION_FILE}")
        sys.exit(1)

    with open(TRANSCRIPTION_FILE, encoding="utf-8") as f:
        full_transcript = f.read()

    # 4) Separar líneas de Agente y Cliente (ya empiezan con “Agente:” / “Cliente:”)
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
            # Si no hay prefijo, se concatena al último hablante
            if agente_lines and (len(agente_lines) > len(cliente_lines)):
                agente_lines[-1] += " " + l
            else:
                cliente_lines[-1] += " " + l

    texto_agente  = " ".join(agente_lines)
    texto_cliente = " ".join(cliente_lines)

    # 5) Tokenizar los dos textos
    tokens_info_agente, sugerencias_ag = tokenizar_texto(
        texto_agente, vocab_catalog, interactivo=INTERACTIVO
    )
    tokens_info_cliente, sugerencias_cl = tokenizar_texto(
        texto_cliente, vocab_catalog, interactivo=INTERACTIVO
    )

    # 6) Si modo interactivo, procesar invitación a agregar nuevos tokens
    if INTERACTIVO:
        combined_sug = {**sugerencias_ag, **sugerencias_cl}
        for tok, opts in combined_sug.items():
            for opt in opts:
                if isinstance(opt, str) and opt.startswith("AGREGAR_COMO("):
                    try:
                        peso = int(opt[len("AGREGAR_COMO(") : -1])
                        if tok not in vocabulario:
                            with open(VOC_LEX_CSV, "a", encoding="utf-8", newline="") as fcsv:
                                writer = csv.writer(fcsv)
                                # Categoría por defecto “otros” si no se preguntó
                                writer.writerow([tok, "otros", str(peso)])
                            vocab_catalog[tok] = ("otros", peso)
                            lexicon[tok] = peso
                            vocabulario.add(tok)
                            print(f"→ Se agregó '{tok}' con puntaje {peso} al vocabulario.")
                    except ValueError:
                        pass

    # 7) Preparar lista de tokens “planos” para el analizador de sentimiento
    tokens_plano = [tok for (tok, _, _) in tokens_info_agente + tokens_info_cliente]

    # 8) Análisis de Sentimiento
    sentiment_report = analizar_sentimiento(tokens_plano, lexicon)

    # 9) Verificación de Protocolo (usando tokens_info_agente y texto_agente)
    protocolo_report = verificar_protocolo(tokens_info_agente, texto_agente.lower())

    # 10) Generar y mostrar reporte
    generar_reporte(sentiment_report, protocolo_report, sugerencias_ag, sugerencias_cl)
