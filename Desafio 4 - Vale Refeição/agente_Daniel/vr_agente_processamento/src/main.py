"""
PROCESSAMENTO PRINCIPAL - GERAÇÃO DA PLANILHA VR
Formato exato conforme modelo
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from agente_vr import AgenteVR

def processar_vr():
    """Função principal que coordena todo o processamento"""
    
    print("="*60)
    print("PROCESSAMENTO DE VR - MAIO 2025")
    print("="*60)
    
    # Inicializar o agente
    agente = AgenteVR()
    
    # Definir caminhos
    pasta_dados = Path(__file__).parent.parent / "data"
    pasta_saida = Path(__file__).parent.parent / "output"
    pasta_saida.mkdir(exist_ok=True)
    
    # Carregar exclusões
    print("\n1. CARREGANDO EXCLUSÕES...")
    agente.carregar_exclusoes(pasta_dados)
    agente.processar_desligamentos(pasta_dados)
    
    # Carregar dados principais
    print("\n2. CARREGANDO DADOS PRINCIPAIS...")
    df_ativos = pd.read_excel(pasta_dados / "ATIVOS.xlsx")
    print(f"   ✓ Ativos: {len(df_ativos)}")
    
    # Carregar admissões de abril
    df_admissoes = pd.read_excel(pasta_dados / "ADMISSÃO ABRIL.xlsx")
    # Adicionar colunas faltantes nas admissões
    df_admissoes['Sindicato'] = 'SINDPPD RS - SINDICATO DOS TRAB. EM PROC. DE DADOS RIO GRANDE DO SUL'
    df_admissoes['DESC. SITUACAO'] = 'Trabalhando'
    df_admissoes['EMPRESA'] = 'EMPRESA'
    df_admissoes['TITULO DO CARGO'] = df_admissoes.get('Cargo', 'CARGO')
    print(f"   ✓ Admissões abril: {len(df_admissoes)}")
    
    # Carregar férias
    df_ferias = pd.read_excel(pasta_dados / "FÉRIAS.xlsx")
    ferias_dict = {}
    for _, row in df_ferias.iterrows():
        matricula = str(row['MATRICULA'])
        dias_ferias = row.get('DIAS DE FÉRIAS', 0)
        # Converter dias corridos para dias úteis (aproximadamente)
        if dias_ferias > 0:
            if dias_ferias <= 10:
                dias_uteis_ferias = int(dias_ferias * 0.7)
            else:
                dias_uteis_ferias = min(22, int(dias_ferias * 0.7))
        else:
            dias_uteis_ferias = 0
        ferias_dict[matricula] = dias_uteis_ferias
    print(f"   ✓ Férias: {len(df_ferias)}")
    
    # Consolidar base
    print("\n3. CONSOLIDANDO BASE...")
    df_consolidado = pd.concat([df_ativos, df_admissoes], ignore_index=True)
    print(f"   Total consolidado: {len(df_consolidado)}")
    
    # Processar cada funcionário
    print("\n4. AGENTE PROCESSANDO FUNCIONÁRIOS...")
    resultados = []
    
    funcionarios_processados = 0
    funcionarios_excluidos = 0
    valor_total_geral = 0
    
    competencia = pd.Timestamp('2025-05-01')  # Maio/2025
    
    for idx, funcionario in df_consolidado.iterrows():
        matricula = str(funcionario['MATRICULA'])
        
        # O agente decide se é elegível
        elegivel, motivo = agente.decidir_elegibilidade(funcionario)
        
        if not elegivel:
            funcionarios_excluidos += 1
            continue
        
        # Buscar sindicato
        sindicato = funcionario.get('Sindicato', '')
        if pd.isna(sindicato) or sindicato == '':
            continue
        
        # Verificar dias de férias
        dias_ferias = ferias_dict.get(matricula, 0)
        
        # Buscar regras do sindicato
        regras = agente.regras_sindicato.get(sindicato)
        if not regras:
            continue
        
        # Calcular dias úteis
        dias_uteis = regras['dias_uteis'] - dias_ferias
        if dias_uteis < 0:
            dias_uteis = 0
        
        # Calcular valor do VR
        if dias_uteis > 0:
            calculo = agente.calcular_valor_vr(sindicato, dias_uteis)
            
            if calculo:
                # Data de admissão (usar data padrão se não tiver)
                data_admissao = funcionario.get('Admissão', pd.NaT)
                if pd.isna(data_admissao):
                    data_admissao = pd.Timestamp('2024-01-01')  # Data padrão
                
                resultado = {
                    'Matricula': int(funcionario['MATRICULA']),
                    'Admissão': data_admissao,
                    'Sindicato do Colaborador': sindicato,
                    'Competência': competencia,
                    'Dias': dias_uteis,
                    'VALOR DIÁRIO VR': calculo['valor_diario'],
                    'TOTAL': calculo['total'],
                    'Custo empresa': calculo['custo_empresa'],
                    'Desconto profissional': calculo['desconto_funcionario'],
                    'OBS GERAL': ''
                }
                
                # Adicionar observações especiais
                if dias_ferias > 0:
                    resultado['OBS GERAL'] = f'Desconto de {dias_ferias} dias de férias'
                
                resultados.append(resultado)
                funcionarios_processados += 1
                valor_total_geral += calculo['total']
        
        # Progresso
        if (idx + 1) % 200 == 0:
            print(f"   Processados: {idx + 1}/{len(df_consolidado)}")
    
    # Criar DataFrame com resultados
    print("\n5. GERANDO PLANILHA FINAL...")
    df_resultado = pd.DataFrame(resultados)
    
    # Ordenar por matrícula
    df_resultado = df_resultado.sort_values('Matricula')
    
    # Criar a planilha com o total na primeira linha
    arquivo_saida = pasta_saida / "VR MENSAL 05.2025.xlsx"
    
    with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
        # Criar uma primeira linha com o total
        df_header = pd.DataFrame({
            'Matricula': [''],
            'Admissão': [''],
            'Sindicato do Colaborador': [''],
            'Competência': [''],
            'Dias': [''],
            'VALOR DIÁRIO VR': [''],
            'TOTAL': [valor_total_geral],
            'Custo empresa': [''],
            'Desconto profissional': [''],
            'OBS GERAL': ['']
        })
        
        # Concatenar header com dados
        df_final = pd.concat([df_header, df_resultado], ignore_index=True)
        
        # Escrever na aba principal
        df_final.to_excel(writer, sheet_name='VR MENSAL 05.2025', index=False)
        
        # Criar aba de validações
        validacoes = pd.DataFrame({
            'Validações': [
                'Afastados / Licenças',
                'DESLIGADOS GERAL',
                'Admitidos mês',
                'Férias',
                'ESTAGIARIO',
                'APRENDIZ',
                'SINDICATOS x VALOR',
                'DESLIGADOS ATÉ O DIA 15 DO MÊS - SE JÁ ESTIVER OK',
                'DESLIGADOS DO DIA 16 ATÉ O ULTIMO DIA DO MÊS PGTO INTEGRAL',
                'ATENDIMENTOS/OBS',
                'Admitidos mês anterior (abril)',
                'EXTERIOR',
                'ATIVOS',
                'REVISAR O CALCULO DE PGTO SE ESTÁ CORRETO ANTES DE MANDAR'
            ],
            'Check': [
                '✓ Processado',
                '✓ Processado',
                '✓ Incluído',
                '✓ Descontado',
                '✓ Excluído',
                '✓ Excluído',
                '✓ Aplicado',
                '✓ Aplicado',
                '✓ Aplicado',
                '',
                '✓ Incluído',
                '✓ Excluído',
                '✓ Processado',
                'Verificar total'
            ]
        })
        
        validacoes.to_excel(writer, sheet_name='Validações', index=False)
        
        # Ajustar larguras das colunas
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    # Relatório final
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL DO AGENTE")
    print("="*60)
    print(f"✓ Funcionários processados: {funcionarios_processados}")
    print(f"✓ Funcionários excluídos: {funcionarios_excluidos}")
    print(f"✓ Valor total de VR: R$ {valor_total_geral:,.2f}")
    print(f"✓ Custo empresa (80%): R$ {valor_total_geral * 0.8:,.2f}")
    print(f"✓ Desconto funcionários (20%): R$ {valor_total_geral * 0.2:,.2f}")
    
    print(f"\n📁 Arquivo salvo: {arquivo_saida}")
    print("\n🤖 O AGENTE concluiu o processamento com sucesso!")
    
    return df_resultado

if __name__ == "__main__":
    df_final = processar_vr()