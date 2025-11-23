#!/bin/bash

echo "======================================"
echo "Configurando Hadoop y cargando datos"
echo "======================================"

# Esperar a que Hadoop esté listo
echo "Esperando a que Hadoop inicie..."
sleep 30

# Verificar que el namenode esté activo
echo "Verificando estado del NameNode..."
docker exec namenode hdfs dfsadmin -safemode wait

# Crear directorios en HDFS
echo "Creando directorios en HDFS..."
docker exec namenode hdfs dfs -mkdir -p /user/hadoop/input
docker exec namenode hdfs dfs -mkdir -p /user/hadoop/output

# Copiar archivos de datos al contenedor namenode
echo "Copiando archivos al contenedor..."
docker cp ./data/yahoo_responses.txt namenode:/tmp/yahoo_responses.txt
docker cp ./data/llm_responses.txt namenode:/tmp/llm_responses.txt
docker cp ./data/stopwords_es.txt namenode:/tmp/stopwords_es.txt

# Subir archivos a HDFS
echo "Subiendo archivos a HDFS..."
docker exec namenode hdfs dfs -put -f /tmp/yahoo_responses.txt /user/hadoop/input/
docker exec namenode hdfs dfs -put -f /tmp/llm_responses.txt /user/hadoop/input/
docker exec namenode hdfs dfs -put -f /tmp/stopwords_es.txt /user/hadoop/input/

# Configurar permisos
echo "Configurando permisos..."
docker exec namenode hdfs dfs -chmod -R 777 /user/hadoop/

# Verificar que los archivos se subieron correctamente
echo ""
echo "Verificando archivos en HDFS:"
docker exec namenode hdfs dfs -ls /user/hadoop/input/

echo ""
echo "======================================"
echo "Configuración completada exitosamente"
echo "======================================"
echo ""
echo "verificar los datos:"
echo "docker exec namenode hdfs dfs -cat /user/hadoop/input/yahoo_responses.txt | head -n 10"