"""
Verificar TODAS as planilhas e suas colunas
arquivo: src/verificar_todas_planilhas.py
"""
import pandas as pd
from pathlib import Path

pasta_dados = Path(__file__).parent.parent / "data"

print("="*60)
print("ANÁLISE COMPLETA DE TODAS AS PLANILHAS")
print("="*60)

# Listar todos os arquivos Excel
arquivos_excel = list(pasta_dados.glob("*.xlsx"))

for arquivo in arquivos_excel:
    print(f"\n📁 {arquivo.name}")
    print("-"*40)
    try:
        df = pd.read_excel(arquivo)
        print(f"Linhas: {len(df)}")
        print(f"Colunas: {df.columns.tolist()}")
        
        # Verificar se tem NOME ou CPF
        if 'NOME' in df.columns or 'Nome' in df.columns:
            print("✓ TEM COLUNA NOME!")
        if 'CPF' in df.columns:
            print("✓ TEM COLUNA CPF!")
            
        # Mostrar amostra se for pequena
        if len(df) < 5:
            print("\nDados completos:")
            print(df)
        elif arquivo.name == "VR MENSAL 05.2025.xlsx":
            print("\nPrimeiras 3 linhas do MODELO esperado:")
            print(df.head(3))
    except Exception as e:
        print(f"Erro ao ler: {e}")