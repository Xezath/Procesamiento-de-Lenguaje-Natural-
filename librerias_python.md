1. **Preprocesamiento de audio**

   * **pydub**: para convertir entre formatos (MP3 ↔ WAV), ajustar sample rate, recortar, normalizar.
   * **librosa**: lectura y análisis básicos de audio (inspección de duración, visualización de espectrogramas).

2. **Transcripción Speech-to-Text**

   * **google-cloud-speech**: cliente oficial de Google Speech-to-Text.
   * **deepspeech** o **coqui-stt**: para reconocimiento local con modelo preentrenado.
   * **SpeechRecognition**: interfaz unificada que permite cambiar entre Google, Sphinx, IBM, etc.
   * **pyaudio** (opcional): si necesitás capturar audio en tiempo real desde micrófono.

3. **Tokenización / Análisis léxico**

   * **re** (librería estándar): `re.findall(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]+", texto)` para extraer palabras.
   * **spaCy** (modelo “es\_core\_news\_sm”): tokenización robusta en español + lematización.
   * **nltk** (modulo `nltk.tokenize.word_tokenize` + `SnowballStemmer`): tokenizador y lematizador español.

4. **Validación de tokens contra diccionario y sugerencias**

   * **pandas**: para cargar/gestionar un `.csv` o `.txt` con el diccionario de palabras en un `DataFrame` o `Series`.
   * **python-Levenshtein** o **rapidfuzz**: para calcular distancia de Levenshtein y proponer las palabras más cercanas.
   * **difflib** (librería estándar): `difflib.get_close_matches` como alternativa ligera.

5. **Análisis de sentimiento**

   * **pandas**: para cargar el lexicón de sentimientos (`sentiment_lexicon.csv`) en un `DataFrame`.
   * **TextBlob** (solo si querés un análisis rápido, aunque orientado al inglés, podrías cargar un lexicón en español).
   * **NLTK** (con `nltk.corpus` y tu propio lexicón): sumar/restar pesos en base a un diccionario personalizado.

6. **Verificación del protocolo de atención**

   * **re**: para buscar patrones de saludo, identificación, palabras prohibidas y despedida mediante expresiones regulares sobre la cadena original.
   * **spaCy Matcher** (opcional): si querés detectar frases compuestas (ej. “buenos días”) mediante patrones de tokens.

7. **Generación de reportes**

   * **pandas**: para volcar resultados en CSV o Excel (`df.to_csv()`, `df.to_excel()`).
   * **json** (librería estándar): para exportar un JSON con el reporte de cada llamada.
   * **openpyxl** o **xlsxwriter**: si necesitás formatos avanzados en Excel (colores, fórmulas).
   * **matplotlib** (opcional): para graficar estadísticas de sentimiento o cumplimiento de protocolo si hacés dashboards.

8. **(Opcional) Interfaz mínima / despliegue**

   * **Flask** o **FastAPI**: para exponer un endpoint que reciba el audio, procese y devuelva el reporte en JSON.
   * **Streamlit**: para levantar un prototipo rápido de interfaz web donde subas un WAV/MP3 y muestres resultados.

Con estas bibliotecas cubrís cada etapa de forma ágil y aprovechas los ecosistemas maduros de Python para procesamiento de audio, NLP y manejo de datos.
