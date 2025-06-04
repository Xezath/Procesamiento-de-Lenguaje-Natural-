import re
from utils import limpiar_palabra

def analizar_sentimiento(texto_transcrito, lexicon_sentimientos):
    """
    Analiza el sentimiento de un texto transcrito.

    Args:
        texto_transcrito (str): La conversación transcrita.
        lexicon_sentimientos (dict): Un diccionario con palabras como claves
                                    y sus puntuaciones de sentimiento como valores.
                                    Ej: {"bueno": 1, "mal": -1}

    Returns:
        dict: Un diccionario con los resultados del análisis de sentimiento.
    """
    palabras = texto_transcrito.split()
    
    puntuacion_total = 0
    palabras_positivas_cont = 0
    palabras_negativas_cont = 0
    
    palabras_positivas_encontradas = []
    palabras_negativas_encontradas = []

    # Variables para rastrear la palabra más positiva y negativa según el PDF [cite: 35]
    # Se inicializan con valores que aseguran que cualquier palabra encontrada los reemplazará.
    palabra_mas_positiva_info = {"palabra": "N/A", "score": float('-inf')}
    palabra_mas_negativa_info = {"palabra": "N/A", "score": float('inf')}

    for palabra_original in palabras:
        palabra = limpiar_palabra(palabra_original)
        if palabra in lexicon_sentimientos:
            score = lexicon_sentimientos[palabra]
            puntuacion_total += score
            
            if score > 0:
                palabras_positivas_cont += 1
                palabras_positivas_encontradas.append({"palabra": palabra, "score": score})
                if score > palabra_mas_positiva_info["score"]:
                    palabra_mas_positiva_info["palabra"] = palabra
                    palabra_mas_positiva_info["score"] = score
            elif score < 0:
                palabras_negativas_cont += 1
                palabras_negativas_encontradas.append({"palabra": palabra, "score": score})
                if score < palabra_mas_negativa_info["score"]:
                    palabra_mas_negativa_info["palabra"] = palabra
                    palabra_mas_negativa_info["score"] = score

    sentimiento_general_str = "Neutral"
    if puntuacion_total > 0:
        sentimiento_general_str = "Positivo" # [cite: 25]
    elif puntuacion_total < 0:
        sentimiento_general_str = "Negativo" # [cite: 26]

    # Ajuste para el caso de que no se encuentren palabras positivas/negativas
    if palabra_mas_positiva_info["score"] == float('-inf'):
        palabra_mas_positiva_info["score"] = "N/A"
    if palabra_mas_negativa_info["score"] == float('inf'):
        palabra_mas_negativa_info["score"] = "N/A"
        
    resultado = {
        "Sentimiento general": f"{sentimiento_general_str} ({puntuacion_total:+})", # [cite: 35]
        "Palabras positivas": palabras_positivas_cont, # [cite: 35]
        "Palabra más positiva": f"{palabra_mas_positiva_info['palabra']}, {palabra_mas_positiva_info['score']}", # [cite: 35]
        "Palabras negativas": palabras_negativas_cont, # [cite: 35]
        "Palabra más negativa": f"{palabra_mas_negativa_info['palabra']}, {palabra_mas_negativa_info['score']}" # [cite: 35]
    }
    
    return resultado

# # --- Ejemplo de Uso ---

# # 1. Definir la tabla de símbolos (lexicon_sentimientos) [cite: 21, 22]
# #    Tomado del ejemplo en el PDF y expandido ligeramente para el ejemplo.
# lexicon = {
#     "hola": 0, # Neutral, pero importante para el contexto
#     "bienvenido": 1,
#     "bueno": 1,
#     "amable": 2,
#     "excelente": 3,
#     "gracias": 1,
#     "ayudar": 1,
#     "resolver": 2,
#     "solución": 2,
#     "consulta": 0,
#     "factura": 0,
#     "problema": -1,
#     "mal": -2,
#     "fatal": -3,
#     "queja": -2,
#     "terrible": -3,
#     "no": -1, # Podría ser contextual, pero como ejemplo simple
#     "cancelar": -1
# }

# # 2. Simular una transcripción de conversación (Asumimos que esta es la entrada)
# #    Esta conversación mezcla elementos positivos y negativos.
# conversacion_ejemplo_1 = """
# Agente: Hola, bienvenido al servicio de Atención al Cliente. Soy un agente amable.
# Cliente: Buenas, tengo un problema con mi factura, es terrible. Necesito una solución.
# Agente: Entiendo su problema. Vamos a resolver esto de forma excelente.
# Cliente: Muchas gracias, eso espero. Su ayuda es buena.
# """

# conversacion_ejemplo_2 = """
# Agente: Hola.
# Cliente: Quiero cancelar mi servicio. Esto es fatal. Muy mal servicio.
# Agente: Lamento escuchar eso.
# """

# conversacion_ejemplo_pdf = """
# Agente: Hola, bienvenido al servicio de Atención al Cliente. ¿Con quién tengo el gusto de hablar?
# Cliente: Buenas, mi nombre es Juan Arias, quiero hacer una consulta acerca de mi factura.
# """ # [cite: 3, 4] (Esta conversación es mayormente neutral según el lexicon de ejemplo del PDF)

# # 3. Analizar el sentimiento
# print("--- Análisis de Conversación Ejemplo 1 (Mezcla) ---")
# resultado_analisis_1 = analizar_sentimiento(conversacion_ejemplo_1, lexicon)
# for clave, valor in resultado_analisis_1.items():
#     print(f"{clave}: {valor}")

# print("\n--- Análisis de Conversación Ejemplo 2 (Negativa) ---")
# resultado_analisis_2 = analizar_sentimiento(conversacion_ejemplo_2, lexicon)
# for clave, valor in resultado_analisis_2.items():
#     print(f"{clave}: {valor}")

# print("\n--- Análisis de Conversación Ejemplo PDF (Neutral/Positiva Leve) ---")
# # Usando el lexicon del PDF para este ejemplo [cite: 22]
# lexicon_pdf_ejemplo = {
#     "bueno": 1,
#     "amable": 2,
#     "problema": -1,
#     "mal": -2,
#     "excelente": 3,
#     "fatal": -3,
#     # Agregamos las palabras del diálogo del PDF, asumiendo son neutrales o ligeramente positivas si son saludos
#     "hola": 1, # Asignando un valor positivo al saludo
#     "bienvenido": 1,
#     "servicio": 0,
#     "atención": 0,
#     "cliente": 0,
#     "gusto": 0, # Podría ser positivo
#     "hablar": 0,
#     "buenas": 1, # Asignando un valor positivo al saludo
#     "nombre": 0,
#     "juan": 0,
#     "arias": 0,
#     "quiero": 0,
#     "hacer": 0,
#     "consulta": 0,
#     "acerca": 0,
#     "factura": 0
# }
# resultado_analisis_pdf = analizar_sentimiento(conversacion_ejemplo_pdf, lexicon_pdf_ejemplo)
# for clave, valor in resultado_analisis_pdf.items():
#     print(f"{clave}: {valor}")