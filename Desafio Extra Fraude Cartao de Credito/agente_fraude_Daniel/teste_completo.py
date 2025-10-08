# teste_completo.py - TESTE COM SESSÃO PERSISTENTE
from agente_eda import perguntar_ao_agente, resetar_agente

def teste_fluxo_completo():
    """🧪 Teste completo do fluxo com sessão persistente"""
    
    print("🧪 TESTE COMPLETO DO AGENTE EDA")
    print("="*50)
    
    # RESET inicial
    print("\n🔄 1. Resetando agente...")
    resetar_agente()
    
    # TESTE 1: Carregar dados
    print("\n📊 2. Carregando dataset de fraude...")
    resposta1 = perguntar_ao_agente("Carregue o arquivo data/creditcard.csv")
    print("✅ Dataset carregado")
    
    # TESTE 2: Pergunta sobre contexto
    print("\n❓ 3. Perguntando sobre o que é a tabela...")
    resposta2 = perguntar_ao_agente("Sobre o que é esta tabela?")
    print(f"🤖 RESPOSTA:\n{resposta2}\n")
    
    # TESTE 3: Pergunta específica - média
    print("\n❓ 4. Perguntando média específica...")
    resposta3 = perguntar_ao_agente("Qual a média da coluna Amount?")
    print(f"🤖 RESPOSTA:\n{resposta3}\n")
    
    # TESTE 4: Outliers específicos
    print("\n❓ 5. Perguntando sobre outliers...")
    resposta4 = perguntar_ao_agente("Quais são os outliers da coluna Amount?")
    print(f"🤖 RESPOSTA:\n{resposta4}\n")
    
    # TESTE 5: Análise temporal
    print("\n❓ 6. Análise temporal...")
    resposta5 = perguntar_ao_agente("Analise as tendências temporais da coluna Time vs Amount")
    print(f"🤖 RESPOSTA:\n{resposta5}\n")
    
    # TESTE 6: Clusters
    print("\n❓ 7. Detecção de clusters...")
    resposta6 = perguntar_ao_agente("Detecte agrupamentos nos dados")
    print(f"🤖 RESPOSTA:\n{resposta6}\n")
    
    print("🎯 TESTE COMPLETO FINALIZADO!")

if __name__ == "__main__":
    teste_fluxo_completo()