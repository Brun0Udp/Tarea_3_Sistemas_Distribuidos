#!/bin/bash

echo "======================================"
echo "Ejecutando Análisis Lingüístico"
echo "======================================"

# Crear directorio de salida si no existe
mkdir -p output/yahoo_results
mkdir -p output/llm_results

# Copiar script Pig al contenedor
echo "Copiando script Pig al contenedor..."
docker cp ./scripts/wordcount_analysis.pig pig:/tmp/wordcount_analysis.pig

# Eliminar resultados anteriores en HDFS si existen
echo "Limpiando resultados anteriores..."
docker exec namenode hdfs dfs -rm -r /user/hadoop/output/yahoo_wordcount 2>/dev/null || true
docker exec namenode hdfs dfs -rm -r /user/hadoop/output/llm_wordcount 2>/dev/null || true

# Análisis de respuestas de Yahoo!
echo ""
echo "======================================"
echo "Analizando respuestas de Yahoo!..."
echo "======================================"
docker exec pig bash -c 'export PIG_HOME=/opt/pig && export PATH=$PATH:$PIG_HOME/bin && export PIG_CLASSPATH=$HADOOP_HOME/etc/hadoop && pig -x mapreduce \
    -param input=/user/hadoop/input/yahoo_responses.txt \
    -param output=/user/hadoop/output/yahoo_wordcount \
    /tmp/wordcount_analysis.pig'

# Análisis de respuestas del LLM
echo ""
echo "======================================"
echo "Analizando respuestas del LLM..."
echo "======================================"
docker exec pig bash -c 'export PIG_HOME=/opt/pig && export PATH=$PATH:$PIG_HOME/bin && export PIG_CLASSPATH=$HADOOP_HOME/etc/hadoop && pig -x mapreduce \
    -param input=/user/hadoop/input/llm_responses.txt \
    -param output=/user/hadoop/output/llm_wordcount \
    /tmp/wordcount_analysis.pig'

# Descargar resultados de HDFS
echo ""
echo "======================================"
echo "Descargando resultados..."
echo "======================================"

# Descargar resultados de Yahoo!
docker exec namenode hdfs dfs -get /user/hadoop/output/yahoo_wordcount/part-r-00000 /tmp/yahoo_results.txt
docker cp namenode:/tmp/yahoo_results.txt ./output/yahoo_results/yahoo_results.txt

# Descargar resultados del LLM
docker exec namenode hdfs dfs -get /user/hadoop/output/llm_wordcount/part-r-00000 /tmp/llm_results.txt
docker cp namenode:/tmp/llm_results.txt ./output/llm_results/llm_results.txt

echo ""
echo "======================================"
echo "Análisis completado exitosamente"
echo "======================================"
echo ""
echo "Resultados guardados en:"
echo "  - output/yahoo_results/yahoo_results.txt"
echo "  - output/llm_results/llm_results.txt"
echo ""
echo "Para ver las top 20 palabras:"
echo "  head -n 20 output/yahoo_results/yahoo_results.txt"
echo "  head -n 20 output/llm_results/llm_results.txt"