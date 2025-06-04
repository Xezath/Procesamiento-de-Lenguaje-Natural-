A continuación encontrarás un desglose detallado del enunciado, un análisis paso a paso de cada requerimiento y varias ideas de cómo abordarlos. Al final, se indica en qué puntos concretos del trabajo cobran relevancia los contenidos de la materia de “Diseño de Compiladores” (análisis léxico, expresiones regulares, autómatas, etc.), y cómo podrían aprovecharse o adaptarse.

---

## 1. Descripción general del problema

El objetivo del Trabajo Práctico es diseñar e implementar un sistema que procese interacciones de un contact center (audio de llamadas), aplique tokenización a las transcripciones y, a partir de esos tokens, realice dos tareas principales:

1. **Análisis de sentimiento** (speech analytics)
2. **Verificación de cumplimiento del protocolo de atención al cliente**

El flujo básico que se propone en el enunciado () es:

1. **Preprocesamiento**
   1.1. Capturar/obtener los audios de llamadas (cliente ↔ agente).
   1.2. Transcribir cada audio a texto (Speech-to-Text).

2. **Tokenización**
   2.1. Dividir la transcripción en lexemas/palabras.
   2.2. Contrastar cada lexema contra una “tabla de símbolos” (diccionario) de palabras en español.
   2.3. Si un lexema NO está en la tabla, pedir validación y, de ser necesario, sugerir correcciones (distancia de Levenshtein, Hamming, etc.).

3. **Fase de análisis (Speech Analytics)**
   3.1. **Análisis de sentimiento**: cada palabra (token) tiene un peso (positiva/negativa). Se suma/ resta para determinar si la interacción fue positiva, negativa o neutral.
   3.2. **Verificación del protocolo de atención**: detectar si el agente cumple ciertas etapas (saludo, identificación del cliente, NO usar palabras rudas, despedida amable), basándose en tokens clave.

4. **Resultados y reporte**
   4.1. Mostrar un resumen de sentimiento (puntaje global, cantidad de palabras positivas/negativas, las más fuertes, etc.).
   4.2. Indicar si el agente siguió el protocolo y, de no ser así, señalar exactamente en qué falló.

---

## 2. Análisis detallado de cada etapa y sugerencias de implementación

A continuación se descompone cada fase, sus desafíos principales y posibles caminos para resolverlos.

### 2.1 Fase 1: Preprocesamiento

#### 2.1.1 Recolección y selección de datos de audio

* **Objetivo**: contar con un “corpus” de grabaciones de llamadas (cliente ↔ agente) que cubra distintos escenarios de sentimiento (positivo, neutro/indiferente, negativo/con quejas).
* **Opciones**:

  * Repositorios públicos (ej. IBM Call Center AI dataset).
  * Grabaciones propias con voces sintéticas (text-to-speech) o male/female.
  * Muestras genuinas (respetando privacidad), idealmente anotadas con la etiqueta de “sentimiento” para poder validar los resultados luego.
* **Formato**: usualmente archivos en formato WAV o MP3 a 16 kHz (teléfonos) o 8 kHz (calidad voz).
* **Desafíos**:

  * **Ruido de fondo** (música, motor, distracciones propias de un centro de contacto).
  * **Voces solapadas** (cliente y agente hablando a la vez).
  * **Variabilidad de acentos/regiones** (en Paraguay, giros y expresiones propias).

**Sugerencia**:
*Utilizar audios de prueba con diferentes calidades y limpiar/filtrar (preprocesamiento acústico mínimo), para asegurarse de que el motor de Speech-to-Text funcione con cierta robustez.*

#### 2.1.2 Transcripción de voz a texto (Speech-to-Text)

* **Herramientas recomendadas**:

  1. **Google Speech-to-Text API** (muy robusto en entornos ruidosos, multilenguaje).
  2. **Mozilla DeepSpeech** (open source, pero quizás menos preciso que Google).
  3. **Amazon Transcribe**.
  4. Cualquier otro motor (ej. IBM Watson, Kaldi, etc.).
* **Puntos a tener en cuenta**:

  * Latencia: si el Trabajo es “offline” (por lotes), basta con pasar cada archivo por un API batch.
  * **Costo**: Google/Amazon cobran por minuto de audio; DeepSpeech o Kaldi requieren GPU/CPU potentes.
  * **Tasa de error**: medir Word Error Rate (WER) en un subconjunto de validación.
  * **Formato de salida**: la mayoría de APIs devuelven la transcripción en texto plano, con timestamp opcional por palabra o por fragmento.
* **Posible flujo**:

  1. Leer cada archivo de audio.
  2. Enviar a la API (o al servidor local de DeepSpeech).
  3. Recuperar la transcripción—idealmente, ya segmentada por turnos “Agente: …” y “Cliente: …”.
  4. Guardar en un archivo de texto o directamente en una estructura (por ejemplo, JSON con campos `{ speaker: "Agente", text: "Hola, bienvenido…", timestamp: ... }`).

> **Relación con la materia**: en sí, la transcripción Speech-to-Text no utiliza directamente gramáticas predictivas ni autómatas. No obstante, puede mencionarse que muchos motores de ASR internamente utilizan modelos de lenguaje (gramáticas probabilísticas) y decodificadores basados en WFST (Weighted Finite State Transducers), pero esto ya sale del alcance práctico del TP. En la materia dieron “traductores dirigidos por sintaxis” (analizador sintáctico), pero aquí no se hace parsing de oraciones, sino sólo reconocimiento de voz.

---

### 2.2 Fase 2: Tokenización / Análisis Léxico

> **Enunciado**:
>
> > “Implementa un tokenizador para segmentar la transcripción en palabras. La misión principal del tokenizador es poder dividir un ejemplo de entrada en palabras o lexemas y catalogarlas según un criterio o patrón. Esta parte puede ser diseñada utilizando estructuras como autómatas finitos y aplicando los conceptos del análisis léxico.”&#x20;

#### 2.2.1 ¿Qué es tokenizar?

Tokenizar significa **recorrer** la cadena de texto (la transcripción) y **separar** fragmentos (lexemas) que correspondan a “unidades mínimas con significado” (palabras, signos de puntuación, códigos, etc.).
En este caso:

* Queremos extraer tokens que sean *palabras en español* (ej. “Hola”, “bienvenido”, “a”, “Atención”, “al”, “Cliente”, …).
* Podríamos **ignorar** mayúsculas/minúsculas (i.e. normalizar todo a minúsculas), o también mantener la correspondencia (por ahora conviene convertir a minúsculas y eliminar tildes/acentos para simplificar).

#### 2.2.2 Estrategias para implementar el tokenizador

1. **Uso directo de librerías NLP de alto nivel**

   * Ejemplo: **NLTK**, **spaCy**, **StanfordCoreNLP**, **OpenNLP**.
   * Ventaja: ya manejan segmentación por palabras, contracciones, apostrofes, emojis, etc.
   * Desventaja: quizá sean “cajón de sastre” y no permiten entender (ni mostrar) cómo funcionan internamente los autómatas o las expresiones regulares.

2. **Implementación manual con expresiones regulares**

   * Definir un patrón regex para “palabra en español” (ej. `[A-Za-zÁÉÍÓÚáéíóúÑñ]+`).
   * Recorrer la cadena texto y extraer cadenas consecutivas de caracteres alfabéticos como tokens.
   * Ventaja: rápido de codificar en Python/Java/JavaScript.
   * Desventaja: no maneja políglotas muy bien (ej. “contraseña”, “d’Onofrio”), pero sirve para un TP.

3. **Diseño de un autómata finito (DFA/AFD)**

   * **Paso 1**: Definir alfabeto: caracteres válidos (letras, espacio, signos de puntuación, dígitos si deseamos tomarlos como tokens aparte).
   * **Paso 2**: Diseñar estados (p. ej., `q0`: estado inicial, `q1`: dentro de una palabra, `q2`: dentro de un número, `q3`: signo de puntuación).
   * **Paso 3**: Definir transiciones:

     * De `q0`, si veo `a–z` o `A–Z` → voy a `q1` (empiezo una palabra).
     * En `q1`, si sigo recibiendo letras → sigo en `q1`; si veo espacio o punto, comillas → cierro token y vuelvo a `q0`.
     * Etc.
   * **Paso 4**: Cada vez que salgo de `q1` a `q0`, recorto el lexema capturado y lo “emito” como token.
   * Ventaja: cumple con la idea de “análisis léxico” y se puede contrastar directamente con la teoría de AFN/DFA y expresiones regulares que vieron en clase.
   * Desaventa: es un poco más laborioso que usar regex simples.

4. **Combinar ambas**:

   * Usar un tokenizador simple con regex, pero documentar que internamente eso equivale a un autómata determinista que reconoce “palabras” como (letra)+, y signos de puntuación como tokens aparte.

#### 2.2.3 Validación de lexemas contra la tabla de símbolos (diccionario de español)

Una vez que tengo un token (por ejemplo, `“bienvenido”`), debo verificar si existe en la **base de datos / tabla de símbolos** (que contendrá palabras válidas en español). Aquí hay varias posibilidades:

1. **Diccionario en memoria**:

   * Cargo un archivo de texto plano (por ejemplo, `diccionario_es.txt`) con una palabra por línea.
   * Uso una estructura tipo **HashSet** (Java) o **set** (Python) para verificar en O(1) si la palabra existe.

2. **Base de datos relacional**:

   * Tener una tabla `Palabras(palabra VARCHAR PRIMARY KEY)`
   * Hacer un `SELECT 1 FROM Palabras WHERE palabra = 'bienvenido';`
   * Pero para un TP, suele ser más sencillo usar un archivo.

> **Cuando un lexema NO está en la tabla**:
>
> * Mostrar la palabra candidata (p.ej. “bitaefeudno” si la transcripción fue muy mala).
> * **Preguntar al usuario (o al operador que está validando) si esa palabra es válida** y a qué token pertenece (por ejemplo: “¿‘bitaefeudno’ corresponde a ‘bienvenido’?”).
> * Si es válida, la agrego a la tabla de símbolos.

#### 2.2.4 Sugerir correcciones para lexemas inválidos

Si el lexema no existe, **probablemente** sea un error de transcripción o un neologismo/región.
Para sugerir reemplazos:

1. **Distancia de Levenshtein** (edición mínima)

   * Calcular la distancia a cada palabra del diccionario (esto es costoso si el diccionario es muy grande, pero se puede optimizar con estructuras como “tri-gram index”, BK-tree, etc.).
   * Sugerir las N palabras con menor distancia (p. ej. ≤ 2).

2. **Distancia Hamming** (solo si las palabras tienen la misma longitud)

   * Se usa cuando solo quiero comparar cadenas de igual longitud; si son muy diferentes de tamaño, no conviene.

3. **Heurística de prefijos/sufijos**

   * Comparar los primeros 2–3 caracteres.

4. **Metodología práctica**:

   * A nivel de TP, con un diccionario de 50 000–100 000 palabras, puedo restringir la búsqueda a palabras que empiecen con la misma letra o con las dos primeras letras del token desconocido, y dentro de eso calcular Levenshtein.

**Salida deseada**: lista de sugerencias:

```
“Lexema detectado: ‘holla’ no está en el diccionario.  
¿Es alguna de estas? -> [“hola” (dist 1), “hallo” (dist 2), “olla” (dist 1)]  
```

> **Conexión con la materia**:
>
> * La parte de “definir un DFA/AFD para reconocer la estructura de un lexema” y “usar expresiones regulares” forma parte de **análisis léxico** (temática central de la cátedra).
> * La “tabla de símbolos” es un concepto clásico en compiladores, aunque en el TP la tabla de símbolos contiene “palabras en español” y no identificadores de un lenguaje de programación; el trasfondo teórico (estructura de datos, búsqueda en tablas) es análogo.

---

### 2.3 Fase 3: Análisis — Speech Analytics

Esta etapa se divide en dos subpasos: **análisis de sentimiento** y **verificación del protocolo de atención**.

#### 2.3.1 Análisis de sentimiento

1. **Tabla de símbolos con ponderaciones**

   * Tener un archivo (p.ej. `sentiment_lexicon.csv`) con dos columnas:

     ```
     Lexema, Ponderación
     bueno, +1
     amable, +2
     problema, -1
     mal, -2
     excelente, +3
     fatal, -3
     ...
     ```
   * Cargarlo en un diccionario en memoria `{ “bueno”: +1, “amable”: +2, … }`.

2. **Algoritmo de cálculo**

   * Inicializar `score = 0`.
   * Para cada token válido en la conversación (tanto del “Agente” como del “Cliente”):

     * Si `token` existe en `sentiment_lexicon`, hacer `score += ponderación`.
     * Además, llevar un conteo de cuántas palabras positivas se encontraron y cuántas negativas.
   * Al finalizar la conversación:

     * Si `score > 0` → interacción ‘mayoritariamente positiva’;
     * Si `score = 0` → interacción neutral;
     * Si `score < 0` → interacción ‘mayoritariamente negativa’.

3. **Reporte intermedio deseado** (basado en el enunciado)

   * Sentimiento general: Positivo (+5) / Negativo (−3) / Neutral (0)
   * Cantidad de palabras positivas: 6
   * Palabra más positiva: “amable” (+2)
   * Cantidad de palabras negativas: 2
   * Palabra más negativa: “mal” (−2)

4. **Posibles mejoras**

   * Separar análisis de agentes vs. clientes (¿las quejas vienen del cliente o del agente?).
   * Incluir bigramas (ej. “muy bueno” podría pesar más que “bueno”).
   * Ponderaciones contextuales (si la palabra “no bueno” aparece, invertir signo).

> **Nota**: El enunciado sugiere un “método simple de cálculo”, por lo que bastará con la suma de pesos. No hace falta diseñar un modelo estadístico complejo.

#### 2.3.2 Verificación del protocolo de atención

El propósito es **chequear** que el agente, en su turno, haya cumplido cuatro fases mínimas:

1. **Saludo inicial**
2. **Identificación del cliente** (preguntar nombre)
3. **No usar palabras rudas**
4. **Despedida amable**

##### a) Saludo inicial

* Definir un conjunto de tokens clave de saludo, por ejemplo:

  ```
  { "hola", "buenos días", "buen día", "buenas tardes", "bienvenido", "estimado cliente", ... }
  ```
* Lógica:

  1. Revisar los primeros N tokens (quizá los primeros 10–20) que pronunció el agente.
  2. Si alguno coincide (exact match o match parcial) con la lista de tokens de saludo → “Fase de saludo: OK”.
  3. Si NO encuentra → “Fase de saludo: Faltante”.

##### b) Identificación del cliente

* Buscar en la conversación (en los turnos del agente) expresiones como:

  ```
  "¿Con quién tengo el gusto de hablar?"
  "¿Me puede decir su nombre?"
  "¿Su nombre, por favor?"
  "¿Cómo se llama?"
  ```
* Técnica:

  * Podrías normalizar a minúsculas y quitar acentos, luego buscar subcadenas (`"quién tengo el gusto"`, `"su nombre"`, etc.).
  * Alternativamente, usar una pequeña gramática de patrones (ej. regex: `\b(¿?me puede decir su nombre)|(¿?cómo se llama)\b`).

##### c) ¿Palabras rudas o prohibidas?

* Tener una lista de “palabras prohibidas” (ej. “inútil”, “tonto”, “idiota”, “asqueroso”, “imposible”, etc., según se defina en el TP).
* Recorrer todos los tokens del agente; si alguno coincide con esa lista → “Uso de palabras rudas: Encontradas \[p.ej. ‘inútil’] → Falla”.
* Si no aparece ninguna → “Uso de palabras rudas: Ninguna detectada”.

##### d) Despedida amable

* Definir tokens clave de cierre, p. ej.

  ```
  { "gracias por su tiempo", "que tenga un buen día", "hasta luego", "que pase excelente día", "cualquier consulta no dude en llamar", … }
  ```
* Buscar esas expresiones en los últimos N tokens (turnos finales del agente).
* Si encuentra alguno → “Despedida amable: OK”.
* Sino → “Despedida amable: Faltante”.

##### e) Cómo iterar con tokenización

* El tokenizador ya dividió la transcripción en tokens (palabras), pero **aquí necesitamos posiblemente**, además de tokens unitarios, reconocer frases/patrones (bigramas/trigramas).
* Propuesta:

  1. **N-gramas**:

     * Construir bigramas y trigramas sobre la lista de tokens: si aparece la secuencia `("buenos","días")` → “saludo OK”.
     * De la misma manera, buscar n-gramas de identificación (`("con","quién","tengo","el","gusto","de","hablar")`).
  2. **Regex sobre la cadena original**:

     * Al generar tokens, también guardamos la cadena original “limpia” (sin timestamps). Podemos aplicar un `regex.search()` para detectar frases completas.
  3. **Matcher de secuencias** (simples loops):

     * Recorrer tokens con un puntero `i`; en cada posición verificar si `(token[i], token[i+1], ..., token[i+k])` coinciden con alguno de los patrones predefinidos.

> **Concepto de gramáticas predictivas/sintaxis**:
> En rigor, aquí NO se está armando un “parser” con gramática de frases del español, sino meramente se verifica la presencia de ciertos tokens o patrones. Por lo tanto, la mayor parte de la teoría de sintaxis predictiva o traducción sintáctica queda **opcional**. La parte que sí coincide con la materia es la **tokenización** (análisis léxico), y la idea de detectar secuencias de tokens clave (podrías pensar en términos de “producciones” muy básicas, pero no hace falta un ARBOL de derivación, solo un “pattern matching”).

---

### 2.4 Fase 4: Resultados y Reporte

#### 2.4.1 Formato de salida para detección de sentimiento

* Un reporte tipo:

  ```
  ===== Análisis de Sentimiento =====
  Sentimiento general: Positivo (+5)
  Número de palabras positivas: 6
  Palabra más positiva: amable (+2)
  Número de palabras negativas: 2
  Palabra más negativa: mal (−2)
  ```

#### 2.4.2 Formato de salida para verificación del protocolo

* Un reporte tipo:

  ```
  === Verificación de Protocolo de Atención ===
  - Fase de saludo: OK
  - Identificación del cliente: OK
  - Uso de palabras rudas: Ninguna detectada
  - Despedida amable: Faltante
  ```

#### 2.4.3 Ideas para la presentación

* **Consola**: mostrar en pantalla los reportes por cada llamada analizada.
* **Archivo CSV/JSON**:

  * Crear un CSV con columnas: `ID_Llamada, Sentimiento_Score, #Positives, #Negatives, Saludo_OK (S/N), Identificación_OK (S/N), PalabrasRudas (lista), Despedida_OK (S/N)`.
* **Interfaz gráfica / sencilla UI** (opcional):

  * Una página web pequeña que permita subir un archivo de audio y, al procesarlo, muestre los reportes.
  * No es requisito, pero “la interfaz es opcional” según el enunciado.

---

## 3. ¿Qué contenidos de Diseño de Compiladores aplican aquí (y en qué parte puntual)?

Aunque el profesor aclaró que **no es obligatorio usar** todos los tópicos vistos, sí se pide que, si alguna parte del TP encaja con la materia, se lo señale. A grandes rasgos:

1. **Análisis léxico (tokenización)**

   * Punto clave donde se aplica directamente:

     * **Reconocimiento de lexemas**: definir qué se considera “palabra” (alfabeto, expresiones regulares).
     * **Diseño de autómatas finitos deterministas (DFA)** que reconozcan la categoría “palabra en español”.
     * **Tablas de símbolos**: normalmente, en compiladores la tabla de símbolos almacena identificadores, variables, etc. En este TP se emplea para almacenar “palabras válidas en español”.
     * **Errores léxicos**: aquí equivalen a “token no reconocido”, se manejan sugiriendo correcciones.

2. **Expresiones regulares y definiciones regulares**

   * Se pueden usar para describir el conjunto de “palabras válidas” (por ejemplo, el regex para token de palabra: `[A-Za-zÁÉÍÓÚáéíóúÑñ]+`).
   * Para detectar patrones de protocolo (ej. saludo o identificación), conviene definir expresiones regulares que capten frases completas, aunque estemos haciendo un análisis más cercano a “string matching”.

3. **Transformaciones de AFN a AFD** (si se implementa el tokenizador con autómatas

   * Se podría diseñar un AFN a partir de la expresión regular `(Letra)+`, convertirlo a un AFD minimizado y codificar las transiciones de forma explícita en un programa.
   * De esta forma, cada caracter que recorre el DFA nos indica si estamos “dentro de una palabra” o “en blanco/espacio” para emitir tokens.

4. **Análisis sintáctico (gramáticas predictivas, parsing)**

   * **Opcional**: en este TP no se pide construir un parser para el lenguaje español (lo cual sería extremadamente complejo).
   * Sin embargo, si se quisiera **reforzar con contenido de la cátedra**, podría proponerse a modo de ejercicio que la parte de “verificación del protocolo” se encarara con una gramática muy simple:

     ```
     SALUDO      → “hola” | “buenos días” | “bienvenido” | …
     IDENTIFICACION → “¿Con quién tengo el gusto de hablar?” | …
     DESPEDIDA   → “gracias por su tiempo” | …
     ```

     Y luego usar un parser predictivo que reconozca dichas producciones en la secuencia de tokens. Pero **esto no es obligatorio**—basta con matching de patrones.

5. **AFN/DFA en el contexto de corrección de léxicos**

   * La técnica de “sugerir correcciones” se basa en **distancias de edición**, que no son directamente temas de compiladores, pero se puede argumentar que, en un compilador, cuando un token no existe se sugiere “posibles símbolos correctos” (por ejemplo, al compilar, si escribiste mal un identificador, el IDE sugiere nombres cercanos).

En síntesis: **la parte central del TP que coincide con la materia** es la **tokenización y el manejo de la tabla de símbolos** (análisis léxico). El resto (speech-to-text, análisis de sentimiento, verificación de protocolo) corresponde más a técnicas de procesamiento de lenguaje natural (NLP) y lógica de aplicación, pero no a gramáticas ni parsing.

---

## 4. Idea de arquitectura global y tecnologías recomendadas

A modo de síntesis, se propone un **esqueleto de implementación** (por ejemplo, en Python, pero podría hacerse en Java, Node.js, etc.):

1. **Módulo `speech_to_text.py`**

   * Función `transcribir_audio(ruta_audio) → lista_de_turnos`.

     * Llama a la API (Google/DeepSpeech).
     * Devuelve algo así como:

       ```json
       [
         { "speaker": "Agente", "text": "Hola, bienvenido al servicio...", "start_time": 0.0, "end_time": 3.2 },
         { "speaker": "Cliente", "text": "Buenas, mi nombre es Juan Arias...", "start_time": 3.2, "end_time": 6.5 },
         ...
       ]
       ```

2. **Módulo `tokenizador.py`**

   * Carga un **diccionario** (set) de palabras en español (`diccionario_es.txt`).
   * Función `tokenizar_turno(turno_texto) → lista_de_tokens`.

     * Opción A: `re.findall(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]+", texto)`.
     * Opción B: implementar un DFA explícito.
   * Función `validar_tokens(tokens) → lista_de_pares (token, es_valido:boolean, sugerencias:[...])`.

     * Para cada token:

       1. Si está en el diccionario → `(token, True, [])`.
       2. Sino → calcular distancias (Levenshtein) y generar sugerencias, devolver `(token, False, ["suger1","suger2"])`.

3. **Módulo `sentimiento.py`**

   * Carga archivo `sentiment_lexicon.csv` → diccionario `{lexema: peso}`.
   * Función `calcular_sentimiento(tokens) → { score_total, positives_count, negative_count, palabra_mas_positiva, palabra_mas_negativa }`.

4. **Módulo `protocolo.py`**

   * Listado de **saludos**, **frases de identificación**, **palabras prohibidas**, **frases de despedida** (los podrás guardar en archivos JSON/CSV para mayor facilidad).
   * Función `verificar_protocolo(lista_turnos_tokenizados) → reporte {saludo: True/False, identificacion: True/False, rudas: [lista], despedida: True/False }`.

     * Para cada fase, usar matching simple de secuencias de tokens o regex sobre la cadena original.

5. **Módulo `main.py`**

   * Ciclo principal que:

     1. Lee la carpeta `audios/`.
     2. Para cada `archivo.wav`:

        * `turnos = transcribir_audio(archivo.wav)`
        * Para cada `turno` en `turnos`:

          * `tokens = tokenizar_turno(turno.texto)`
          * `validaciones = validar_tokens(tokens)` (opcional: interactividad si existe token inválido).
        * `sent_report = calcular_sentimiento(tokens_agente + tokens_cliente)`
        * `protocol_report = verificar_protocolo(turnos_tokenizados_por_speaker)`
        * Imprimir o guardar los dos reportes.

6. **Informe final (PDF)**

   * **Sección 1**: Descripción del problema, tecnologías elegidas, estructura general.
   * **Sección 2**: Detalle de cada fase, decisiones de diseño, mejoras propuestas.
   * **Sección 3**: Código fuente (resumido en apéndice o link a repositorio).
   * **Sección 4**: Ejemplo con un caso de prueba real (capturas de pantalla del reporte).
   * **Sección 5**: Observaciones (limitaciones del motor ASR, casos no cubiertos, etc.).

---

## 5. Posibles retos y consideraciones adicionales

1. **Ruido y errores de transcripción**

   * Si la transcripción falla (p. ej. “hoja” en lugar de “hola”), el sistema de tokenización no hallará “hoja” en el diccionario y sugerirá “hola” (distancia Levenshtein = 1).
   * Esto se traduce en que el análisis de sentimiento y protocolo puede verse afectado: un “hola” mal detectado puede omitir el saludo.

2. **Variantes de una misma palabra**

   * Palabras con mayúsculas/minúsculas o tildes (e.g. “acción” vs. “accion”). Conviene normalizar todo a minúsculas y quitar acentos antes de buscar en el diccionario.

3. **Formas verbales conjugadas**

   * Si nuestro diccionario incluye únicamente forma infinitiva (“resolver”, “ayudar”) pero el ASR produce “resolvió”, “ayudó”, “resuelvo”, etc., no estará en el diccionario.
   * Solución:

     * Incluir lematización o “stemmers” (p. ej. usar NLTK o SnowballStemmer para español) y guardar en la tabla de símbolos las formas simples (lematizadas).
     * O bien extender el diccionario con las conjugaciones más comunes.

4. **Detección de frases completas (bigramas/trigramas)**

   * Para reconocer “buenos días” como un saludo completo hace falta combinar dos tokens (“buenos” + “días”).
   * Táctica: en la lista de saludos, incluir tanto tokens de una sola palabra (“hola”) como expresiones de varias palabras (“buenos días”). Al tokenizar, calzar n-gramas para ver si alguno de esos patrones aparece.

5. **Casos grises en protocolo**

   * ¿Qué pasa si el agente dice algo antirreglamentario (“gracias por su tiempo, qué tenga buen día”) en el medio de la conversación, pero no al final? Técnicamente está “presente”, pero quizá no en la parte de cierre.
   * Decidir “ventana de búsqueda”: por ejemplo, solo verificar los últimos 20 tokens del agente para la despedida.

6. **Interactividad para lexemas desconocidos**

   * El enunciado sugiere “Preguntar si la palabra es válida y a qué token pertenece”. Esto implica que, durante la ejecución, el sistema podría pausar y mostrar algo como:

     ```
     Lexema no reconocido: “porsupuesto”  
     Es válido? (S/N)  
     Si es válido, ¿a qué palabra del diccionario corresponde o qué token desea asignar?  
     ```
   * En la práctica, para un TP, conviene reemplazar esto por un “modo batch” donde los lexemas desconocidos se van guardando en un archivo de “pendientes” para revisarlos manualmente luego.

---

## 6. Resumen de puntos clave y vínculos con la materia

1. **Punto principal donde aparece la materia “Diseño de Compiladores”**:

   * **Tokenización (análisis léxico)**:

     * **Expresiones regulares** para definir qué es una palabra.
     * Diseño de **DFA/AFD** (o AFN convertido a AFD) que reconozca “(letra)+”.
     * **Tabla de símbolos** para almacenar las palabras válidas (idéntico al concepto clásico de un compilador).
     * Manejo de “errores léxicos” (tokens no reconocidos), con sugerencias mediante algoritmos de distancia.

2. **Gramáticas, parsing y análisis sintáctico**

   * **Opcional**: en el trabajo no se construye un parser que valide sintácticamente las frases, pero podría esbozarse que la verificación de protocolo utiliza “pequeñas gramáticas” (producciones mínimas) para detectar frases completas (p.ej. `SALUDO → buenos días | hola`).
   * No es necesario armar tablas LL(1) ni analizar derivaciones; basta con matching de patrones.

3. **Definiciones regulares y AFN**

   * La definición de “token de palabra” es una expresión regular del tipo `[A-Za-zÁÉÍÓÚáéíóúÑñ]+`.
   * Convertir esa expresión a un **AFN** y luego, si se desea, a un **AFD** minimizado.

4. **Conexión más amplia con compilación**

   * El TP ilustra cómo un “analizador léxico” puede usarse fuera del contexto de lenguajes de programación, en NLP.
   * Conceptos de errores léxicos y de “sugerencias de corrección” tienen paralelo con IDEs que subrayan variables mal escritas y sugieren nombres cercanos.

---

## 7. Posibles extensiones o mejoras (más allá del enunciado)

1. **Uso de un stemmer o lematizador en español**

   * Con NLTK o spaCy, obtener la forma base de la palabra (“lematizar”) para normalizar mejor el análisis de sentimiento (p.ej. “amabilidad” → “amable”).

2. **Modelo de sentimiento más avanzado**

   * Emplear una lexicón más amplio (p. ej. **Spanish SentiWordNet**), o incluso entrenar un clasificador (Máquina de Soporte Vectorial, Naive Bayes) si se dispone de un corpus etiquetado.

3. **Uso de un parser leve (chunking)**

   * En lugar de solo n-gramas, usar un modelo de chunker (p.ej. detectar “NP” (frases nominales) para verificar que la oración “¿Con quién tengo el gusto de hablar?” encaje en la categoría “solicitud de nombre).

4. **Generar métricas de calidad y puntuación global de agentes**

   * Calcular promedios de sentimiento de cada agente a lo largo de X llamadas.
   * Asignar “score final de calidad” que combine sentimiento + cumplimiento de protocolo.

5. **Interfaz web/Gráficas**

   * Mostrar dashboards con gráficas de barras: % de llamadas positivas vs. negativas, porcentaje de agentes que cumplen protocolo, etc. (requiere usar bibliotecas tipo matplotlib o D3.js).

---

## 8. Conclusión

* **Punto fuerte del TP**: combina técnicas de **procesamiento de lenguaje natural** con conceptos de **diseño de compiladores** (específicamente análisis léxico y tablas de símbolos).

* **Recomendación**:

  1. **Enmarcar en la memoria** la parte de tokenización como “análisis léxico” (explicar brevemente cómo se define el token, la expresión regular y, opcionalmente, el DFA resultante).
  2. Para el resto de fases (speech-to-text, análisis de sentimiento, verificación de protocolo), explicar las **decisiones arquitectónicas** (por qué se escogió Google Speech-to-Text, cómo se diseña la tabla de ponderaciones, etc.).
  3. Registrar claramente las **limitaciones** (p.ej. si el ASR falla con voces con eco, o si el diccionario no cubre todas las variantes dialectales).

* **Resumen de los contenidos de la materia**:

  * **Análisis Léxico**: Tokenización (DFA/expresiones regulares), tabla de símbolos, manejo de errores léxicos.
  * **Definiciones regulares**: expresiones regulares para reconocer palabras en español.
  * **AFN/AFD**: posibilidad de explicar conceptualmente cómo se representaría el tokenizador como un autómata.
  * **Análisis sintáctico**: opcionalmente, para mostrar que se podría usar un parser “ligero” para verificar secuencias de tokens que correspondan a un saludo, etc., aunque en la práctica baste con n-gramas o regex.

Con este análisis tienes un **mapa completo** para encarar el Trabajo:

* Conoces cada fase, cómo vincularla con contenido teórico de la materia y qué alternativas existen para implementarlas.
* Ahora podrás pasar a escribir el código (Python o Java), preparar el informe (documento PDF) y, finalmente, realizar la defensa presencial mostrando ejemplos concretos de llamadas, tokenización, reportes de sentimiento y verificación de protocolo.

¡Mucho éxito en la implementación!
