"""
Verificar todas as abas da planilha VR MENSAL 05.2025.xlsx
"""
import pandas as pd
from pathlib import Path

pasta_dados = Path(__file__).parent.parent / "data"
arquivo_modelo = pasta_dados / "VR MENSAL 05.2025.xlsx"

print("="*60)
print("ANÁLISE DE TODAS AS ABAS DO MODELO")
print("="*60)

# Abrir o arquivo Excel para ver todas as abas
excel_file = pd.ExcelFile(arquivo_modelo)

print(f"\nAbas encontradas: {excel_file.sheet_names}")

# Analisar cada aba
for sheet_name in excel_file.sheet_names:
    print(f"\n{'='*60}")
    print(f"ABA: {sheet_name}")
    print("="*60)
    
    df = pd.read_excel(arquivo_modelo, sheet_name=sheet_name)
    
    print(f"Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
    print(f"Colunas: {df.columns.tolist()}")
    
    # Se for a aba principal, mostrar mais detalhes
    if "VR Mensal" in sheet_name or sheet_name == excel_file.sheet_names[0]:
        # Tentar identificar o header correto
        df_clean = pd.read_excel(arquivo_modelo, sheet_name=sheet_name, skiprows=1)
        print(f"\nColunas (pulando primeira linha): {df_clean.columns.tolist()}")
        
        # Remover linhas completamente vazias
        df_clean = df_clean.dropna(how='all')
        print(f"Linhas com dados: {len(df_clean)}")
        
        # Verificar se tem a coluna TOTAL
        if 'TOTAL' in df_clean.columns:
            total = df_clean['TOTAL'].sum()
            print(f"Soma da coluna TOTAL: R$ {total:,.2f}")
        
        # Mostrar primeiras linhas válidas
        print("\nPrimeiras 3 linhas válidas:")
        print(df_clean.head(3))
    
    # Se for aba de validação
    if "valida" in sheet_name.lower():
        print("\nConteúdo da aba de validação:")
        print(df.head(20))  # Mostrar mais linhas da validação

print("\n" + "="*60)
print("IMPORTANTE: Devemos gerar a saída no mesmo formato da aba principal!")