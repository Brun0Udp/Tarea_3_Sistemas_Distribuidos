#!/usr/bin/env python3
"""
Script de visualización de resultados del análisis lingüístico
Genera gráficos comparativos simplificados
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path
import numpy as np

# Configuración de estilo
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    plt.style.use('seaborn-darkgrid')
sns.set_palette("husl")

def load_results(filepath):
    """Carga los resultados del análisis desde un archivo"""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                word, count = parts
                data.append({'word': word, 'count': int(count)})
    return pd.DataFrame(data)

def create_comparison_chart(yahoo_df, llm_df, top_n=30):
    """Crea gráfico de barras comparativo"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    
    # Yahoo top 
    yahoo_top = yahoo_df.head(top_n)
    ax1.barh(yahoo_top['word'][::-1], yahoo_top['count'][::-1], color='steelblue')
    ax1.set_xlabel('Frecuencia', fontsize=12)
    ax1.set_title(f'Top {top_n} Palabras - Yahoo!', fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # LLM top 
    llm_top = llm_df.head(top_n)
    ax2.barh(llm_top['word'][::-1], llm_top['count'][::-1], color='coral')
    ax2.set_xlabel('Frecuencia', fontsize=12)
    ax2.set_title(f'Top {top_n} Palabras - LLM', fontsize=14, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/comparison_bar_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Gráfico de barras comparativo guardado")

def create_common_words_comparison(yahoo_df, llm_df, top_n=20):
    """Crea gráfico de comparación de palabras comunes"""
    # palabras comunes
    yahoo_dict = dict(zip(yahoo_df['word'], yahoo_df['count']))
    llm_dict = dict(zip(llm_df['word'], llm_df['count']))
    
    common_words = set(yahoo_dict.keys()) & set(llm_dict.keys())
    
    # Crear dataframe con palabras comunes y sus frecuencias
    comparison_data = []
    for word in common_words:
        comparison_data.append({
            'word': word,
            'yahoo_freq': yahoo_dict[word],
            'llm_freq': llm_dict[word],
            'total_freq': yahoo_dict[word] + llm_dict[word]
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    comparison_df = comparison_df.sort_values('total_freq', ascending=False).head(top_n)
    
    # Crear gráfico de barras agrupadas
    fig, ax = plt.subplots(figsize=(14, 10))
    
    x = np.arange(len(comparison_df))
    width = 0.35
    
    bars1 = ax.barh(x - width/2, comparison_df['yahoo_freq'], width, 
                     label='Yahoo!', color='steelblue', alpha=0.8)
    bars2 = ax.barh(x + width/2, comparison_df['llm_freq'], width, 
                     label='LLM', color='coral', alpha=0.8)
    
    ax.set_xlabel('Frecuencia', fontsize=12)
    ax.set_ylabel('Palabra', fontsize=12)
    ax.set_title(f'Top {top_n} Palabras Comunes - Comparación de Frecuencias', 
                 fontsize=14, fontweight='bold')
    ax.set_yticks(x)
    ax.set_yticklabels(comparison_df['word'])
    ax.legend(fontsize=11)
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/common_words_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Gráfico de palabras comunes guardado ({len(comparison_df)} palabras)")
    
    return comparison_df

def create_common_words_scatter(yahoo_df, llm_df):
    """Crea gráfico de dispersión de palabras comunes"""
    # Encontrar palabras comunes
    yahoo_dict = dict(zip(yahoo_df['word'], yahoo_df['count']))
    llm_dict = dict(zip(llm_df['word'], llm_df['count']))
    
    common_words = set(yahoo_dict.keys()) & set(llm_dict.keys())
    
    yahoo_freqs = [yahoo_dict[word] for word in common_words]
    llm_freqs = [llm_dict[word] for word in common_words]
    
    # Crear gráfico de dispersión
    fig, ax = plt.subplots(figsize=(12, 10))
    
    scatter = ax.scatter(yahoo_freqs, llm_freqs, alpha=0.6, s=100, c='purple', edgecolors='black', linewidth=1)
    
    # Línea diagonal o frecuencias iguales
    max_freq = max(max(yahoo_freqs), max(llm_freqs))
    ax.plot([0, max_freq], [0, max_freq], 'r--', alpha=0.5, linewidth=2, label='Frecuencias iguales')
    
    ax.set_xlabel('Frecuencia en Yahoo!', fontsize=12)
    ax.set_ylabel('Frecuencia en LLM', fontsize=12)
    ax.set_title('Dispersión de Frecuencias - Palabras Comunes', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # palabras más frecuentes
    top_words = sorted(common_words, key=lambda w: yahoo_dict[w] + llm_dict[w], reverse=True)[:10]
    for word in top_words:
        ax.annotate(word, (yahoo_dict[word], llm_dict[word]), 
                   fontsize=9, alpha=0.7, xytext=(5, 5), 
                   textcoords='offset points')
    
    plt.tight_layout()
    plt.savefig('output/common_words_scatter.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Gráfico de dispersión guardado")

def create_vocabulary_overlap(yahoo_df, llm_df):
    """Crea gráfico de solapamiento de vocabulario"""
    yahoo_words = set(yahoo_df['word'])
    llm_words = set(llm_df['word'])
    
    common = len(yahoo_words & llm_words)
    yahoo_only = len(yahoo_words - llm_words)
    llm_only = len(llm_words - yahoo_words)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Diagrama de Venn simplificado con barras
    categories = ['Solo Yahoo!', 'Comunes', 'Solo LLM']
    counts = [yahoo_only, common, llm_only]
    colors = ['steelblue', 'purple', 'coral']
    
    bars = ax.bar(categories, counts, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax.set_ylabel('Número de palabras únicas', fontsize=12)
    ax.set_title('Solapamiento de Vocabulario', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Añadir valores en las barras
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{count:,}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('output/vocabulary_overlap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Gráfico de solapamiento guardado")
    
    return yahoo_only, common, llm_only

def create_comparison_table(yahoo_df, llm_df, top_n=50):
    """Crea tabla comparativa en CSV"""
    yahoo_top = yahoo_df.head(top_n)[['word', 'count']].rename(columns={'word': 'palabra_yahoo', 'count': 'freq_yahoo'})
    llm_top = llm_df.head(top_n)[['word', 'count']].rename(columns={'word': 'palabra_llm', 'count': 'freq_llm'})
    
    comparison = pd.concat([yahoo_top.reset_index(drop=True), llm_top.reset_index(drop=True)], axis=1)
    comparison.index = range(1, len(comparison) + 1)
    comparison.index.name = 'ranking'
    
    comparison.to_csv('output/comparison_table.csv', encoding='utf-8')
    print("✓ Tabla comparativa guardada en CSV")

def main():
    """Función principal"""
    print("\n" + "="*70)
    print("GENERACIÓN DE VISUALIZACIONES Y REPORTES")
    print("="*70 + "\n")
    
    # Crear directorio de salida
    Path('output').mkdir(exist_ok=True)
    
    # Cargar resultados
    print("Cargando resultados...")
    try:
        yahoo_df = load_results('output/yahoo_results/yahoo_results.txt')
        llm_df = load_results('output/llm_results/llm_results.txt')
    except FileNotFoundError as e:
        print(f"\n Error: No se encontraron los archivos de resultados")
        print(f"   {e}")
        print("\n Asegúrate de haber ejecutado primero:")
        print("   ./scripts/run_analysis.sh")
        return
    
    print(f"  Yahoo!: {len(yahoo_df):,} palabras únicas")
    print(f"  LLM: {len(llm_df):,} palabras únicas\n")
    
    # Generar visualizaciones
    print("Generando visualizaciones...")
    create_comparison_chart(yahoo_df, llm_df)
    yahoo_only, common, llm_only = create_vocabulary_overlap(yahoo_df, llm_df)
    
    # Gráficos de palabras comunes
    print("\nGenerando gráficos de palabras comunes...")
    common_df = create_common_words_comparison(yahoo_df, llm_df)
    create_common_words_scatter(yahoo_df, llm_df)
    
    # Generar reportes
    print("\nGenerando tablas CSV...")
    create_comparison_table(yahoo_df, llm_df)
    
    # Guardar tabla de palabras comunes
    common_df.to_csv('output/common_words_table.csv', encoding='utf-8', index=False)
    print("✓ Tabla de palabras comunes guardada en CSV")
    
    print("\n" + "="*70)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("="*70)
    print("\nArchivos generados en la carpeta 'output/':")
    print(" comparison_bar_chart.png - Top 30 cada fuente")
    print(" common_words_comparison.png - Top 20 palabras comunes")
    print(" common_words_scatter.png - Dispersión de frecuencias")
    print(" vocabulary_overlap.png - Solapamiento de vocabulario")
    print(" comparison_table.csv - Tabla comparativa Top 50")
    print(" common_words_table.csv - Tabla de palabras comunes")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()