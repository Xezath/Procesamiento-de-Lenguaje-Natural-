#!/usr/bin/env python3

import warnings

# ---------------- FILTRO DE WARNINGS ----------------

# 1) Silenciar aviso de Lightning al actualizar checkpoint
warnings.filterwarnings(
    "ignore",
    message=".*Lightning automatically upgraded.*",
    category=UserWarning
)

# 2) Silenciar aviso de Pyannote.audio versión antigua
warnings.filterwarnings(
    "ignore",
    message=".*Model was trained with pyannote\\.audio.*",
    category=UserWarning
)

# 3) Silenciar aviso de PyTorch versión antigua en Pyannote
warnings.filterwarnings(
    "ignore",
    message=".*Model was trained with torch.*",
    category=UserWarning
)

# 4) Silenciar aviso de SpeechBrain sobre symlinks en Windows
warnings.filterwarnings(
    "ignore",
    message=".*Requested Pretrainer collection using symlinks.*",
    category=UserWarning
)

# 5) Silenciar aviso de Whisper “flash attention”
warnings.filterwarnings(
    "ignore",
    message=".*Torch was not compiled with flash attention.*",
    category=UserWarning
)

# ----------------------------------------------------

import os
import sys
import tempfile
import torch

import whisper
from pydub import AudioSegment
from pyannote.audio import Pipeline

def cargar_whisper_medium():
    """
    Carga el modelo Whisper "medium" en GPU si está disponible, sino en CPU.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🔄 Cargando Whisper 'medium' en dispositivo: {device}")
    modelo = whisper.load_model("medium", device=device)
    return modelo

def diarizar_audio(ruta_wav: str):
    """
    Usa Pyannote.audio para obtener segmentos diarizados.
    Requiere que la variable de entorno HUGGINGFACE_TOKEN esté presente.
    Retorna lista de tuplas: (start_s, end_s, speaker_label).
    """
    print("🔍 Iniciando diarización con Pyannote...")
    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    if not hf_token:
        print("[ERROR] No se encontró la variable HUGGINGFACE_TOKEN.")
        sys.exit(1)

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization",
        use_auth_token=hf_token
    )
    diarization = pipeline({"uri": "llamada_tp1", "audio": ruta_wav})

    segmentos = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segmentos.append((turn.start, turn.end, speaker))
    return segmentos

def transcribir_fragmento_whisper(fragmento: AudioSegment, modelo) -> str:
    """
    Exporta un fragmento de AudioSegment a WAV temporal y llama a Whisper para transcribirlo.
    Devuelve el texto transcrito.
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        ruta_temp = tmp.name
        fragmento.export(ruta_temp, format="wav")

    try:
        resultado = modelo.transcribe(ruta_temp, language="es")
        texto = resultado.get("text", "").strip()
    except Exception as e:
        texto = f"[ERROR TRANSCRIPCIÓN: {e}]"
    finally:
        os.remove(ruta_temp)

    return texto

def transcribir_con_diarizacion(ruta_wav: str, modelo):
    """
    Flujo principal:
      1. Carga el WAV completo con pydub.
      2. Diariza para obtener segmentos (start_s, end_s, speaker).
      3. Por cada segmento, recorta el AudioSegment y transcribe con Whisper.
      4. Guarda en 'transcripcion.txt' cada turno en el formato específico:
            Rol: texto
         donde Rol es "Agente" o "Cliente", asignados según el orden
         en que aparecen los speakers en la diarización.
    """
    print("🎧 Cargando audio con pydub...")
    audio_completo = AudioSegment.from_wav(ruta_wav)
    segmentos = diarizar_audio(ruta_wav)

    # Mapeo de etiquetas del diarizador a roles "Agente"/"Cliente"
    speaker_map = {}
    next_role = "Agente"

    # Abrir archivo de salida
    with open("transcripcion.txt", "w", encoding="utf-8") as f:
        print("\n🎤 Transcribiendo y guardando en 'transcripcion.txt'...\n")
        for start_s, end_s, speaker in segmentos:
            # Asignar rol si es la primera vez que aparece este speaker
            if speaker not in speaker_map:
                speaker_map[speaker] = next_role
                next_role = "Cliente" if next_role == "Agente" else "Agente"

            role = speaker_map[speaker]
            start_ms = int(start_s * 1000)
            end_ms   = int(end_s   * 1000)
            fragmento = audio_completo[start_ms:end_ms]

            minutos = int(start_s // 60)
            segundos = start_s % 60
            timestamp = f"{minutos:02d}:{segundos:05.2f}"

            print(f"▶ [{timestamp}] [{role}] …", end="", flush=True)
            texto = transcribir_fragmento_whisper(fragmento, modelo)
            print(" listo.")

            # Escribir línea en el archivo de forma específica para tokenización:
            #   <Rol>: <texto>\n
            linea = f"{role}: {texto}\n"
            f.write(linea)

    print("\n✅ Transcripción completa guardada en 'transcripcion.txt'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python transcribir.py ruta_archivo.wav")
        sys.exit(1)

    ruta_wav = sys.argv[1]
    if not os.path.isfile(ruta_wav):
        print(f"[ERROR] No se encontró el archivo: {ruta_wav}")
        sys.exit(1)

    modelo_whisper = cargar_whisper_medium()
    transcribir_con_diarizacion(ruta_wav, modelo_whisper)
