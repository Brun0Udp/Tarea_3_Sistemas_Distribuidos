#!/bin/bash

echo "=========================================="
echo "INICIO RÁPIDO - Hadoop"
echo "=========================================="

# Verificar que existan los datos
if [ ! -f "data/yahoo_responses.txt" ] || [ ! -f "data/llm_responses.txt" ]; then
    echo ""
    echo " No se encontraron los archivos de datos"
    echo ""
    echo " Opciones:"
    echo "  1. Si tienes archivos CSV, ejecuta primero:"
    echo "     python scripts/clean_data.py"
    echo ""
    echo "  2. O coloca manualmente los archivos:"
    echo "     - data/yahoo_responses.txt"
    echo "     - data/llm_responses.txt"
    echo ""
    exit 1
fi

echo ""
echo "Paso 1: Deteniendo contenedores previos..."
docker-compose down 2>/dev/null

echo ""
echo "Paso 2: Iniciando Hadoop..."
docker-compose up -d

echo ""
echo "Paso 3: Esperando a que Hadoop esté listo..."
sleep 30

echo ""
echo "Paso 4: Configurando Hadoop y cargando datos..."
chmod +x scripts/setup_hadoop.sh
./scripts/setup_hadoop.sh

echo ""
echo "=========================================="
echo "   Sistema listo para ejecutar análisis"
echo "=========================================="
echo ""
echo "Siguiente paso:"
echo "  ./scripts/run_analysis.sh"
echo ""