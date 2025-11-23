#!/usr/bin/env python3

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

def process_yahoo_file(input_file, output_file, max_responses=None):
    """Procesa archivo de Yahoo (una línea por respuesta)"""
    print(f"\nProcesando Yahoo: {input_file}")
    
    responses = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                cleaned = clean_text(line)
                if cleaned and len(cleaned) > 5:  # Filtrar líneas muy cortas
                    responses.append(cleaned)
        
        # Limitar al máximo si se especifica
        if max_responses and len(responses) > max_responses:
            print(f"    Se encontraron {len(responses)} respuestas, limitando a {max_responses}")
            responses = responses[:max_responses]
        
        # Verificar mínimo de 15 respuestas
        if len(responses) < 15:
            print(f"     ERROR: Se encontraron solo {len(responses)} respuestas")
            print(f"     Se requieren al menos 15 respuestas válidas")
            return None, len(responses)
        
        # Guardar archivo limpio
        with open(output_file, 'w', encoding='utf-8') as f:
            for response in responses:
                f.write(response + '\n')
        
        print(f"  ✓ Archivo Yahoo limpio guardado: {output_file}")
        print(f"    Total de respuestas: {len(responses)}")
        
        # Mostrar muestra
        if responses:
            print(f"    Muestra (primeras 3 respuestas):")
            for i, resp in enumerate(responses[:3], 1):
                preview = resp[:80] + "..." if len(resp) > 80 else resp
                print(f"      {i}. {preview}")
        
        return True, len(responses)
    
    except Exception as e:
        print(f" Error procesando {input_file}: {e}")
        return None, 0

def process_llm_file(input_file, output_file, max_responses=None):
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
        
        # Limitar al máximo si se especifica
        if max_responses and len(responses) > max_responses:
            print(f" Se encontraron {len(responses)} respuestas, limitando a {max_responses}")
            responses = responses[:max_responses]
        
        # Verificar mínimo de 15 respuestas
        if len(responses) < 15:
            print(f"    ERROR: Se encontraron solo {len(responses)} respuestas")
            print(f"    Se requieren al menos 15 respuestas válidas")
            return None, len(responses)
        
        # Guardar archivo limpio
        with open(output_file, 'w', encoding='utf-8') as f:
            for response in responses:
                f.write(response + '\n')
        
        print(f"  ✓ Archivo LLM limpio guardado: {output_file}")
        print(f"    Total de respuestas: {len(responses)}")
        
        # Mostrar muestra
        if responses:
            print(f"    Muestra (primeras 3 respuestas):")
            for i, resp in enumerate(responses[:3], 1):
                preview = resp[:100] + "..." if len(resp) > 100 else resp
                print(f"      {i}. {preview}")
        
        return True, len(responses)
    
    except Exception as e:
        print(f" Error procesando {input_file}: {e}")
        import traceback
        traceback.print_exc()
        return None, 0

def verify_output_files():
    """Verifica que los archivos de salida sean correctos"""
    print("\n" + "=" * 70)
    print("VERIFICACIÓN DE ARCHIVOS GENERADOS")
    print("=" * 70)
    
    yahoo_file = Path('data/yahoo_responses.txt')
    llm_file = Path('data/llm_responses.txt')
    
    yahoo_count = 0
    llm_count = 0
    
    if yahoo_file.exists():
        with open(yahoo_file, 'r', encoding='utf-8') as f:
            yahoo_count = len(f.readlines())
        print(f"\n✓ Yahoo: {yahoo_count} respuestas")
    else:
        print("\n No se encontró data/yahoo_responses.txt")
    
    if llm_file.exists():
        with open(llm_file, 'r', encoding='utf-8') as f:
            llm_count = len(f.readlines())
        print(f"✓ LLM: {llm_count} respuestas")
    else:
        print(" No se encontró data/llm_responses.txt")
    
    if yahoo_file.exists() and llm_file.exists():
        if yahoo_count >= 15 and llm_count >= 15:
            if yahoo_count == llm_count:
                print(f"\n Ambos archivos tienen exactamente {yahoo_count} respuestas (BALANCEADO)")
            else:
                print(f"\n  Los archivos tienen diferente cantidad de respuestas:")
                print(f"    Yahoo: {yahoo_count}, LLM: {llm_count}")
            return True
        else:
            print(f"\n ERROR: Uno o ambos archivos tienen menos de 15 respuestas")
            print(f"    Yahoo: {yahoo_count}, LLM: {llm_count}")
            return False
    
    return False

def main():
    print("=" * 70)
    print("LIMPIEZA DE DATOS PARA HADOOP/PIG")
    print("Mínimo 15 respuestas por archivo, balanceado a la cantidad menor")
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
    
    # FASE 1: Procesar archivos sin límite para contar respuestas
    print("\n" + "=" * 70)
    print("FASE 1: Contando respuestas disponibles")
    print("=" * 70)
    
    # Procesar Yahoo (sin límite)
    yahoo_success, yahoo_count = process_yahoo_file(yahoo_input, 'data/yahoo_responses_temp.txt')
    
    # Procesar LLM (sin límite)
    llm_success, llm_count = process_llm_file(llm_input, 'data/llm_responses_temp.txt')
    
    # Verificar que ambos tengan al menos 15
    if yahoo_count < 15 or llm_count < 15:
        print("\n" + "=" * 70)
        print("ERROR: NO HAY SUFICIENTES RESPUESTAS")
        print("=" * 70)
        print(f"\nRespuestas encontradas:")
        print(f"  Yahoo: {yahoo_count} (mínimo requerido: 15)")
        print(f"  LLM: {llm_count} (mínimo requerido: 15)")
        print("\n Agrega más respuestas a los archivos CSV y vuelve a ejecutar")
        
        # Limpiar archivos temporales
        Path('data/yahoo_responses_temp.txt').unlink(missing_ok=True)
        Path('data/llm_responses_temp.txt').unlink(missing_ok=True)
        return
    
    # FASE 2: Balancear a la cantidad mínima
    min_responses = min(yahoo_count, llm_count)
    
    print("\n" + "=" * 70)
    print("FASE 2: Balanceando archivos")
    print("=" * 70)
    print(f"\nCantidad de respuestas:")
    print(f"  Yahoo: {yahoo_count}")
    print(f"  LLM: {llm_count}")
    print(f"  Mínimo: {min_responses}")
    print(f"\n✓ Ambos archivos se limitarán a {min_responses} respuestas")
    
    # Procesar nuevamente con límite
    yahoo_success, _ = process_yahoo_file(yahoo_input, 'data/yahoo_responses.txt', max_responses=min_responses)
    llm_success, _ = process_llm_file(llm_input, 'data/llm_responses.txt', max_responses=min_responses)
    
    # Limpiar archivos temporales
    Path('data/yahoo_responses_temp.txt').unlink(missing_ok=True)
    Path('data/llm_responses_temp.txt').unlink(missing_ok=True)
    
    # Hacer backup de archivos originales
    if yahoo_success:
        try:
            backup = f"data/original/{Path(yahoo_input).name}.backup"
            Path(yahoo_input).rename(backup)
            print(f"\n Backup Yahoo guardado: {backup}")
        except:
            pass
    
    if llm_success:
        try:
            backup = f"data/original/{Path(llm_input).name}.backup"
            Path(llm_input).rename(backup)
            print(f"Backup LLM guardado: {backup}")
        except:
            pass
    
    # Verificar resultados
    if yahoo_success and llm_success:
        if verify_output_files():
            print("\n" + "=" * 70)
            print("PROCESO COMPLETADO EXITOSAMENTE")
            print("=" * 70)
            print(f"\nArchivos balanceados: {min_responses} respuestas cada uno")
            print("\nSiguiente paso:")
            print("  1. Verifica los archivos:")
            print("     head -n 5 data/yahoo_responses.txt")
            print("     head -n 5 data/llm_responses.txt")
            print("\n  2. Si todo se ve bien, ejecuta:")
            print("     chmod +x scripts/setup_hadoop.sh")
            print("     ./scripts/setup_hadoop.sh")
        else:
            print("\n" + "=" * 70)
            print(" PROCESO COMPLETADO CON ADVERTENCIAS")
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