import pandas as pd
import os

# Corrigir o caminho - usar caminho absoluto é mais seguro
import sys
from pathlib import Path

# Encontrar a pasta raiz do projeto
pasta_raiz = Path(__file__).parent.parent
pasta_dados = pasta_raiz / "data"

print(f"📂 Procurando arquivos em: {pasta_dados}")

# Verificar se a pasta existe e listar arquivos
if pasta_dados.exists():
    arquivos = list(pasta_dados.glob("*.xlsx"))
    print(f"📋 Arquivos Excel encontrados: {len(arquivos)}")
    for arquivo in arquivos:
        print(f"  - {arquivo.name}")
else:
    print("❌ Pasta data não encontrada!")
    sys.exit(1)

# Tentar ler a planilha de ativos
arquivo_ativos = pasta_dados / "ATIVOS.xlsx"

if arquivo_ativos.exists():
    print(f"\n✅ Lendo arquivo: {arquivo_ativos.name}")
    df_ativos = pd.read_excel(arquivo_ativos)
    
    # Ver todos os sindicatos únicos
    if 'Sindicato' in df_ativos.columns:
        sindicatos_unicos = df_ativos['Sindicato'].unique()
        
        print("\n🔍 Sindicatos encontrados na planilha ATIVOS:")
        print("="*50)
        for i, sindicato in enumerate(sindicatos_unicos, 1):
            print(f"{i}. {sindicato}")
        
        # Contar funcionários por sindicato
        print("\n📊 Quantidade por sindicato:")
        print("="*50)
        contagem = df_ativos['Sindicato'].value_counts()
        for sindicato, qtd in contagem.items():
            print(f"{sindicato}: {qtd} funcionários")
    else:
        print("\n❌ Coluna 'Sindicato' não encontrada!")
        print("Colunas disponíveis:", df_ativos.columns.tolist())
else:
    print(f"❌ Arquivo {arquivo_ativos} não encontrado!")