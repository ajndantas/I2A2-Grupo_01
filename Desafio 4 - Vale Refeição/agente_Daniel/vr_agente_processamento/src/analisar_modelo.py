"""
Analisar a estrutura da planilha modelo VR MENSAL 05.2025.xlsx
"""
import pandas as pd
from pathlib import Path

pasta_dados = Path(__file__).parent.parent / "data"

print("="*60)
print("ANÁLISE DO MODELO VR MENSAL 05.2025")
print("="*60)

# Ler a planilha pulando a primeira linha (que parece ter o total)
arquivo_modelo = pasta_dados / "VR MENSAL 05.2025.xlsx"

# Primeiro, vamos ver as primeiras linhas sem processar
df_raw = pd.read_excel(arquivo_modelo, header=None)
print("\nPrimeiras 5 linhas (sem processar):")
print(df_raw.head())

# Agora vamos ler com a linha 1 como header
df_modelo = pd.read_excel(arquivo_modelo, skiprows=1)
print("\n" + "="*60)
print("Colunas identificadas:")
print(df_modelo.columns.tolist())

print("\n" + "="*60)
print("Primeiras 5 linhas com dados:")
# Remover linhas vazias
df_modelo_limpo = df_modelo.dropna(how='all')
print(df_modelo_limpo.head())

print("\n" + "="*60)
print("Informações sobre os dados:")
print(f"Total de linhas com dados: {len(df_modelo_limpo)}")
print(f"Tipos de dados:")
for col in df_modelo_limpo.columns:
    print(f"  {col}: {df_modelo_limpo[col].dtype}")

# Verificar o total
if 'Valor Total' in df_modelo_limpo.columns:
    total = df_modelo_limpo['Valor Total'].sum()
    print(f"\nTotal calculado: R$ {total:,.2f}")

# Ver valores únicos em algumas colunas
if 'Tipo' in df_modelo_limpo.columns:
    print(f"\nValores únicos em 'Tipo': {df_modelo_limpo['Tipo'].unique()}")