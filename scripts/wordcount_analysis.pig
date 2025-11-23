-- Script de análisis de frecuencia de palabras con Apache Pig
-- Parámetros: input (archivo de entrada) y output (directorio de salida)

-- Registrar funciones necesarias
REGISTER '/opt/pig/lib/piggybank.jar';

-- Cargar stopwords
stopwords = LOAD '/user/hadoop/input/stopwords_es.txt' USING PigStorage() AS (word:chararray);

-- Cargar datos de entrada
raw_data = LOAD '$input' USING PigStorage('\n') AS (line:chararray);

-- Tokenización: dividir cada línea en palabras
tokenized = FOREACH raw_data GENERATE FLATTEN(TOKENIZE(LOWER(line))) AS word;

-- Limpieza: eliminar puntuación y caracteres especiales
cleaned = FOREACH tokenized GENERATE REGEX_EXTRACT(word, '([a-záéíóúñü]+)', 1) AS word;

-- Filtrar palabras nulas o vacías
filtered_nulls = FILTER cleaned BY word IS NOT NULL AND word != '';

-- Filtrar palabras demasiado cortas (menos de 3 caracteres)
filtered_short = FILTER filtered_nulls BY SIZE(word) >= 3;

-- Eliminar stopwords mediante anti-join
filtered_stopwords = JOIN filtered_short BY word LEFT OUTER, stopwords BY word;
filtered_final = FILTER filtered_stopwords BY stopwords::word IS NULL;
words_only = FOREACH filtered_final GENERATE filtered_short::word AS word;

-- Agrupar por palabra y contar frecuencias
grouped = GROUP words_only BY word;
word_counts = FOREACH grouped GENERATE 
    group AS word, 
    COUNT(words_only) AS count;

-- Ordenar por frecuencia descendente
sorted = ORDER word_counts BY count DESC;

-- Guardar resultados
STORE sorted INTO '$output' USING PigStorage('\t');

-- Opcional: Mostrar las top 20 palabras
top_20 = LIMIT sorted 20;
DUMP top_20;