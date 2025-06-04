

import re

def verificar_protocolo(texto_transcrito):
    texto = texto_transcrito.lower()

    saludos = [
        r"\bhola\b", r"\bbuen[oa]s?\b", r"\bbuen d[ií]a\b",
        r"\bbuenas tardes\b", r"\bbuenas noches\b"
    ]
    saludo_ok = any(re.search(pat, texto) for pat in saludos)

    patrones_identificacion = [
        r"con qui[ée]n tengo el gusto", r"me puede decir su nombre",
        r"su nombre es", r"dígame su nombre", r"podr[ií]a darme su nombre", r"quien habla"
    ]
    identificacion_ok = any(re.search(pat, texto) for pat in patrones_identificacion)

    palabras_rudas = {
        "inútil", "tonto", "idiota", "estúpido", "imbécil", "asco", "burro", "pendejo", "cerdo", "cabrón", "mierda"
    }
    ruda_encontrada = [pr for pr in palabras_rudas if re.search(rf"\b{re.escape(pr)}\b", texto)]

    patrones_despedida = [
        r"gracias por su tiempo", r"que tenga un buen d[ií]a", r"gracias por llamarnos",
        r"hasta luego", r"\bad[ií]os\b", r"ante cualquier duda"
    ]
    despedida_ok = any(re.search(pat, texto) for pat in patrones_despedida)

    return {
        "Saludo inicial": saludo_ok,
        "Identificación del cliente": identificacion_ok,
        "Palabras rudas": ruda_encontrada,
        "Despedida amable": despedida_ok
    }
