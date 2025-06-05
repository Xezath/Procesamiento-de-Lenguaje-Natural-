from typing import List, Tuple, Dict

def verificar_protocolo(
    tokens_info_agente: List[Tuple[str,str,int]],
    texto_agente_completo: str
) -> Dict[str, object]:
    """
    Verifica si el agente cumplió las fases del protocolo usando la categoría pragmática
    de cada token y, cuando hace falta, inspecciona el texto normalizado:

      - Saludo inicial: basta con que aparezca algún token con categoría "saludo".
      - Identificación: verifica si hay token con categoría "identificacion".
      - Uso de palabras rudas: detecta tokens cuya categoría sea "palabra_ruda".
      - Despedida amable: basta con un token de categoría "despedida".

    Retorna un diccionario con:
      {
        "saludo": {"ok": bool},
        "identificacion": {"ok": bool},
        "rudas": {"lista": List[str]},
        "despedida": {"ok": bool}
      }
    """
    # 1) Saludo inicial
    saludo_ok = any(categoria == "saludo" for (_, categoria, _) in tokens_info_agente)

    # 2) Identificación: basta con que exista algún token con categoría "identificacion"
    identificacion_ok = any(categoria == "identificacion" for (_, categoria, _) in tokens_info_agente)

    # 3) Palabras rudas: todos los tokens cuya categoría sea "palabra_ruda"
    palabras_rudas_usadas = [tok for (tok, categoria, _) in tokens_info_agente if categoria == "palabra_ruda"]

    # 4) Despedida amable: basta con que exista algún token de categoría "despedida"
    despedida_ok = any(categoria == "despedida" for (_, categoria, _) in tokens_info_agente)

    return {
        "saludo":         {"ok": saludo_ok},
        "identificacion": {"ok": identificacion_ok},
        "rudas":          {"lista": palabras_rudas_usadas},
        "despedida":      {"ok": despedida_ok}
    }
