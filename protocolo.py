import re
from typing import List, Dict
from unidecode import unidecode

def verificar_protocolo(
    tokens_agente: List[str],
    texto_agente_completo: str
) -> Dict[str, object]:
    """
    Verifica si el agente cumplió las fases del protocolo:
      - Saludo inicial: detecta tokens de saludo en 'tokens_agente'.
      - Identificación: busca patrones genéricos en el texto normalizado.
      - Uso de palabras rudas: detecta tokens prohibidos.
      - Despedida amable: busca frases de despedida en el texto normalizado.

    Retorna un diccionario con:
      {
        "saludo": {"ok": bool},
        "identificacion": {"ok": bool},
        "rudas": {"lista": List[str]},
        "despedida": {"ok": bool}
      }
    """
    # 1) Fase de saludo (basta con que aparezca alguno de estos tokens)
    saludos_tokens = {
        "hola", "buenos", "buen", "bienvenido", "buenas", "alto", "hola", "buenas",
        "tarde", "noche", "gracias"
    }
    saludo_ok = any(tok in saludos_tokens for tok in tokens_agente)

    # 2) Fase de identificación: patrones genéricos (texto normalizado sin tildes)
    ta = unidecode(texto_agente_completo.lower())
    identificacion_ok = False
    for pattern in [
        r"con quien tengo el gusto",
        r"como se llama",
        r"su nombre",
        r"me puede decir su nombre"
    ]:
        if re.search(pattern, ta):
            identificacion_ok = True
            break

    # 3) Palabras rudas: si el agente usa alguna de estas, se registra
    prohibidas = {"inutil", "tonto", "idiota", "asqueroso", "imbecil"}
    palabras_rudas_usadas = [tok for tok in tokens_agente if tok in prohibidas]

    # 4) Despedida amable: buscar frases completas (texto normalizado)
    despedida_ok = False
    for phrase in [
        "gracias por su tiempo",
        "que tenga un buen dia",
        "hasta luego",
        "cualquier consulta no dude en llamar"
    ]:
        if phrase in ta:
            despedida_ok = True
            break

    return {
        "saludo": {"ok": saludo_ok},
        "identificacion": {"ok": identificacion_ok},
        "rudas": {"lista": palabras_rudas_usadas},
        "despedida": {"ok": despedida_ok}
    }
