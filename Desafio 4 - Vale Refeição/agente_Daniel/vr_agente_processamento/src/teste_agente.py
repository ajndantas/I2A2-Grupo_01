"""
Teste do agente com dados reais
"""
from agente_vr import AgenteVR
from pathlib import Path

# Criar o agente
print("="*60)
print("TESTE DO AGENTE VR")
print("="*60)

agente = AgenteVR()

# Definir caminho dos dados
pasta_dados = Path(__file__).parent.parent / "data"

print(f"\nCarregando exclusões de: {pasta_dados}")
agente.carregar_exclusoes(pasta_dados)
agente.processar_desligamentos(pasta_dados)

# Testar cálculo para cada sindicato
print("\n" + "="*60)
print("TESTE DE CÁLCULO POR SINDICATO")
print("="*60)

for nome_sindicato, regras in agente.regras_sindicato.items():
    print(f"\nSindicato: {regras['estado']}")
    print(f"Nome: {nome_sindicato[:50]}...")
    
    resultado = agente.calcular_valor_vr(nome_sindicato, regras['dias_uteis'])
    if resultado:
        print(f"  Valor diário: R$ {resultado['valor_diario']}")
        print(f"  Dias úteis: {resultado['dias']}")
        print(f"  Total: R$ {resultado['total']}")
        print(f"  Empresa paga: R$ {resultado['custo_empresa']}")
        print(f"  Funcionário paga: R$ {resultado['desconto_funcionario']}")

# Gerar relatório
agente.gerar_relatorio()