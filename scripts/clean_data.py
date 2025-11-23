#!/usr/bin/env python3
"""
Script para limpiar y convertir archivos CSV al formato correcto para Hadoop/Pig
Procesa exactamente 15 respuestas usando comillas como delimitadores
"""

import re
import csv
from pathlib import Path

def clean_text(text):
    """Limpia el texto removiendo formato especial"""
    if not text or text.strip() == "":
        return None
    
    # Remover numeración al inicio (ej: "1", "2.", "1.", etc.)
    text = re.sub(r'^\s*\d+\.?\s*', '', text)
    
    # Remover asteriscos de formato markdown (**texto**)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    
    # Remover asteriscos sueltos
    text = text.replace('*', '')
    
    # Remover comillas extras al inicio y final
    text = text.strip('"').strip("'").strip()
    
    # Normalizar espacios múltiples en uno solo
    text = re.sub(r'\s+', ' ', text)
    
    # Remover espacios al inicio y final
    text = text.strip()
    
    return text if text else None

def process_yahoo_file(input_file, output_file):
    """Procesa archivo de Yahoo (una línea por respuesta)"""
    print(f"\nProcesando Yahoo: {input_file}")
    
    responses = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                cleaned = clean_text(line)
                if cleaned and len(cleaned) > 5:  # Filtrar líneas muy cortas
                    responses.append(cleaned)
        
        # Verificar que tengamos 15 respuestas
        if len(responses) != 15:
            print(f" Advertencia: Se esperaban 15 respuestas, se encontraron {len(responses)}")
        
        # Guardar archivo limpio
        with open(output_file, 'w', encoding='utf-8') as f:
            for response in responses:
                f.write(response + '\n')
        
        print(f"✓ Archivo Yahoo limpio guardado: {output_file}")
        print(f"  Total de respuestas: {len(responses)}")
        
        # Mostrar muestra
        if responses:
            print(f" Muestra (primeras 3 respuestas):")
            for i, resp in enumerate(responses[:3], 1):
                preview = resp[:80] + "..." if len(resp) > 80 else resp
                print(f"    {i}. {preview}")
        
        return True
    
    except Exception as e:
        print(f"Error procesando {input_file}: {e}")
        return False

def process_llm_file(input_file, output_file):
    """Procesa archivo LLM (respuestas delimitadas por comillas)"""
    print(f"\nProcesando LLM: {input_file}")
    
    responses = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraer todas las respuestas delimitadas por comillas
        # Patrón: buscar contenido entre comillas, puede tener múltiples líneas
        pattern = r'"([^"]*(?:\n[^"]*)*)"'
        matches = re.findall(pattern, content)
        
        # Limpiar cada respuesta encontrada
        for match in matches:
            cleaned = clean_text(match)
            if cleaned and len(cleaned) > 5:  # Filtrar respuestas muy cortas
                responses.append(cleaned)
        
        # Si no encontramos respuestas con el patrón anterior, intentar CSV
        if len(responses) == 0:
            print("  Intentando parseo alternativo con CSV reader...")
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, quotechar='"', skipinitialspace=True)
                for row in reader:
                    if row:
                        # Buscar la celda con más contenido (probablemente la respuesta)
                        for cell in row:
                            if cell and len(cell) > 20:  # Filtrar celdas pequeñas (números, etc)
                                cleaned = clean_text(cell)
                                if cleaned and len(cleaned) > 5:
                                    responses.append(cleaned)
        
        # Limitar a 15 respuestas (por si acaso encontramos más)
        if len(responses) > 15:
            print(f"Se encontraron {len(responses)} respuestas, tomando las primeras 15")
            responses = responses[:15]
        
        # Verificar que tengamos 15 respuestas
        if len(responses) != 15:
            print(f"Advertencia: Se esperaban 15 respuestas, se encontraron {len(responses)}")
            print(f"Considera revisar el formato del archivo manualmente")
        
        # Guardar archivo limpio
        with open(output_file, 'w', encoding='utf-8') as f:
            for response in responses:
                f.write(response + '\n')
        
        print(f"Archivo LLM limpio guardado: {output_file}")
        print(f" Total de respuestas: {len(responses)}")
        
        # Mostrar muestra
        if responses:
            print(f"  Muestra (primeras 3 respuestas):")
            for i, resp in enumerate(responses[:3], 1):
                preview = resp[:100] + "..." if len(resp) > 100 else resp
                print(f"    {i}. {preview}")
        
        return True
    
    except Exception as e:
        print(f"Error procesando {input_file}: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_output_files():
    """Verifica que los archivos de salida sean correctos"""
    print("\n" + "=" * 70)
    print("VERIFICACIÓN DE ARCHIVOS GENERADOS")
    print("=" * 70)
    
    yahoo_file = Path('data/yahoo_responses.txt')
    llm_file = Path('data/llm_responses.txt')
    
    if yahoo_file.exists():
        with open(yahoo_file, 'r', encoding='utf-8') as f:
            yahoo_lines = f.readlines()
        print(f"\n✓ Yahoo: {len(yahoo_lines)} respuestas")
        if len(yahoo_lines) != 15:
            print(f"Se esperaban 15, se encontraron {len(yahoo_lines)}")
    else:
        print("\n No se encontró data/yahoo_responses.txt")
    
    if llm_file.exists():
        with open(llm_file, 'r', encoding='utf-8') as f:
            llm_lines = f.readlines()
        print(f"✓ LLM: {len(llm_lines)} respuestas")
        if len(llm_lines) != 15:
            print(f" Se esperaban 15, se encontraron {len(llm_lines)}")
    else:
        print("\n No se encontró data/llm_responses.txt")
    
    if yahoo_file.exists() and llm_file.exists():
        if len(yahoo_lines) == 15 and len(llm_lines) == 15:
            print("\n Ambos archivos tienen exactamente 15 respuestas")
            return True
        else:
            print("\n  Los archivos no tienen el número esperado de respuestas")
            return False
    
    return False

def main():
    print("=" * 70)
    print("LIMPIEZA DE DATOS PARA HADOOP/PIG (15 RESPUESTAS)")
    print("=" * 70)
    
    # Crear directorios si no existen
    Path('data').mkdir(exist_ok=True)
    Path('data/original').mkdir(exist_ok=True)
    
    # Buscar archivos de entrada
    yahoo_input = None
    llm_input = None
    
    # Posibles nombres para archivos de Yahoo
    yahoo_candidates = [
        'data/yahoo_answers.csv',
        'data/yahoo_responses.csv',
        'data/yahoo.csv',
        'data/yahoo_answers.txt',
        'data/yahoo_responses.txt',
    ]
    
    # Posibles nombres para archivos de LLM
    llm_candidates = [
        'data/llm_answers.csv',
        'data/llm_responses.csv',
        'data/llm.csv',
        'data/llm_answers.txt',
        'data/llm_responses.txt',
    ]
    
    # Buscar archivo de Yahoo
    for candidate in yahoo_candidates:
        if Path(candidate).exists():
            yahoo_input = candidate
            print(f"\n✓ Encontrado archivo Yahoo: {candidate}")
            break
    
    # Buscar archivo de LLM
    for candidate in llm_candidates:
        if Path(candidate).exists():
            llm_input = candidate
            print(f"✓ Encontrado archivo LLM: {candidate}")
            break
    
    if not yahoo_input or not llm_input:
        print("\n No se encontraron los archivos necesarios")
        print("\n Archivos esperados en la carpeta 'data/':")
        print("  - yahoo_answers.csv (o yahoo_responses.csv)")
        print("  - llm_answers.csv (o llm_responses.csv)")
        print("\n Coloca tus archivos CSV en la carpeta 'data/' con estos nombres")
        return
    
    # Procesar archivos
    success_count = 0
    
    # Procesar Yahoo
    if process_yahoo_file(yahoo_input, 'data/yahoo_responses.txt'):
        success_count += 1
        # Hacer backup del original
        try:
            backup = f"data/original/{Path(yahoo_input).name}.backup"
            Path(yahoo_input).rename(backup)
            print(f"  Backup guardado: {backup}")
        except:
            pass
    
    # Procesar LLM
    if process_llm_file(llm_input, 'data/llm_responses.txt'):
        success_count += 1
        # Hacer backup del original
        try:
            backup = f"data/original/{Path(llm_input).name}.backup"
            Path(llm_input).rename(backup)
            print(f"  Backup guardado: {backup}")
        except:
            pass
    
    # Verificar resultados
    if success_count == 2:
        if verify_output_files():
            print("\n" + "=" * 70)
            print(" PROCESO COMPLETADO EXITOSAMENTE")
            print("=" * 70)
            print("\n Siguiente paso:")
            print("  1. Verifica los archivos:")
            print("     head -n 5 data/yahoo_responses.txt")
            print("     head -n 5 data/llm_responses.txt")
            print("\n  2. Si todo se ve bien, ejecuta:")
            print("     chmod +x scripts/setup_hadoop.sh")
            print("     ./scripts/setup_hadoop.sh")
        else:
            print("\n" + "=" * 70)
            print("  PROCESO COMPLETADO CON ADVERTENCIAS")
            print("=" * 70)
            print("\n Revisa los archivos manualmente antes de continuar")
    else:
        print("\n" + "=" * 70)
        print(" PROCESO INCOMPLETO")
        print("=" * 70)
        print("\n Revisa los errores arriba y corrige los archivos de entrada")
    
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()