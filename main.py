from analizador_de_sentimiento import analizar_sentimiento
from tokenizacion import tokenizar_texto
from protocolo import verificar_protocolo

# Definir lexicon para análisis de sentimiento
lexicon = {
    "hola": 0, "bienvenido": 1, "bueno": 1, "amable": 2, "excelente": 3,
    "gracias": 1, "ayudar": 1, "resolver": 2, "solución": 2, "consulta": 0,
    "factura": 0, "problema": -1, "mal": -2, "fatal": -3, "queja": -2,
    "terrible": -3, "no": -1, "cancelar": -1
}

# Vocabulario ejemplo
vocabulario = set(lexicon.keys()).union({
    "servicio", "cliente", "con", "quien", "tengo", "el", "gusto", "hablar",
    "buenas", "mi", "nombre", "juan", "arias", "quiero", "hacer", "acerca", "de"
})

# Transcripción de conversación
texto_transcrito = """
Agente: Hola, bienvenido al servicio de Atención al Cliente.
Cliente: Buenas, mi nombre es Juan Arias, quiero hacer una consulta acerca de mi factura.
Agente: Entiendo su problema. Vamos a resolver esto de forma excelente.
Cliente: Muchas gracias, eso espero. Su ayuda es buena.
"""

# 1. Tokenizar
print("\n--- Tokenización ---")
tokens = tokenizar_texto(texto_transcrito, vocabulario)

# 2. Análisis de Sentimiento
print("\n--- Análisis de Sentimiento ---")
resultado_sentimiento = analizar_sentimiento(texto_transcrito, lexicon)
for k, v in resultado_sentimiento.items():
    print(f"{k}: {v}")

# 3. Verificación del Protocolo
print("\n--- Verificación del Protocolo ---")
resultado_protocolo = verificar_protocolo(texto_transcrito)
for k, v in resultado_protocolo.items():
    print(f"{k}: {v}")
