import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import holidays
import warnings
warnings.filterwarnings('ignore')

class VRCalculator:
    def __init__(self):
        # Período de competência: 15/04/2025 à 15/05/2025
        self.inicio_competencia = datetime(2025, 4, 15)
        self.fim_competencia = datetime(2025, 5, 15)
        
        # Dicionário para armazenar os DataFrames das planilhas
        self.planilhas = {}
        
        # Valores de VR por sindicato (valores exemplo - devem ser ajustados conforme planilha)
        self.valores_vr_sindicato = {
            'SINDICATO_EXEMPLO_1': 35.00,
            'SINDICATO_EXEMPLO_2': 32.00,
            # Adicionar outros sindicatos conforme necessário
        }
        
    def carregar_planilhas(self, caminho_base='.'):
        """Carrega todas as planilhas necessárias"""
        arquivos = {
            'ativos': 'ATIVOS.xlsx',
            'vr_mensal': 'VR MENSAL 05.2025.xlsx',
            'ferias': 'FÉRIAS.xlsx',
            'afastamentos': 'AFASTAMENTOS.xlsx',
            'desligamentos': 'DESLIGAMENTOS.xlsx',
            'exterior': 'EXTERIOR.xlsx',
            'admissao_abril': 'ADMISSÃO ABRIL.xlsx',
            'estagios': 'ESTÁGIOS.xlsx',
            'aprendiz': 'APRENDIZ.xlsx'
        }
        
        for nome, arquivo in arquivos.items():
            try:
                caminho = Path(caminho_base) / arquivo
                if caminho.exists():
                    self.planilhas[nome] = pd.read_excel(caminho)
                    print(f"✓ Carregado: {arquivo}")
                else:
                    print(f"⚠ Arquivo não encontrado: {arquivo}")
                    self.planilhas[nome] = pd.DataFrame()
            except Exception as e:
                print(f"❌ Erro ao carregar {arquivo}: {str(e)}")
                self.planilhas[nome] = pd.DataFrame()
    
    def obter_feriados_periodo(self, estado='BR'):
        """Obtém feriados nacionais e estaduais para o período"""
        # Feriados nacionais do Brasil para 2025
        br_holidays = holidays.Brazil(years=2025)
        
        feriados_periodo = []
        data_atual = self.inicio_competencia
        
        while data_atual <= self.fim_competencia:
            # Feriados nacionais
            if data_atual.date() in br_holidays:
                feriados_periodo.append(data_atual)
            data_atual += timedelta(days=1)
        
        # Adicionar feriados estaduais específicos se necessário
        # Exemplo: Dia de São Jorge (RJ) - 23/04
        if estado == 'RJ':
            dia_sao_jorge = datetime(2025, 4, 23)
            if self.inicio_competencia <= dia_sao_jorge <= self.fim_competencia:
                feriados_periodo.append(dia_sao_jorge)
        
        return feriados_periodo
    
    def contar_dias_uteis(self, data_inicio, data_fim, estado='BR'):
        """Conta dias úteis entre duas datas, excluindo fins de semana e feriados"""
        if data_inicio > data_fim:
            return 0
        
        feriados = self.obter_feriados_periodo(estado)
        feriados_dates = [f.date() for f in feriados]
        
        dias_uteis = 0
        data_atual = data_inicio
        
        while data_atual <= data_fim:
            # Verifica se não é sábado (5) nem domingo (6)
            if data_atual.weekday() < 5:  # Segunda=0, ..., Sexta=4
                # Verifica se não é feriado
                if data_atual.date() not in feriados_dates:
                    dias_uteis += 1
            data_atual += timedelta(days=1)
        
        return dias_uteis
    
    def calcular_dias_uteis_matricula(self, matricula, data_admissao=None, sindicato=None):
        """Calcula dias úteis para uma matrícula específica considerando todas as regras"""
        
        # Estado baseado no sindicato (simplificado - ajustar conforme necessário)
        estado = 'BR'  # Default
        if sindicato and 'RJ' in str(sindicato).upper():
            estado = 'RJ'
        elif sindicato and 'SP' in str(sindicato).upper():
            estado = 'SP'
        
        # Verificar se é estagiário ou aprendiz (TOTAL = 0)
        if not self.planilhas['estagios'].empty:
            if matricula in self.planilhas['estagios']['matricula'].values:
                return 0
        
        if not self.planilhas['aprendiz'].empty:
            if matricula in self.planilhas['aprendiz']['matricula'].values:
                return 0
        
        # Verificar afastamentos sem retorno
        if not self.planilhas['afastamentos'].empty:
            afastamento = self.planilhas['afastamentos'][
                self.planilhas['afastamentos']['matricula'] == matricula
            ]
            if not afastamento.empty and pd.isna(afastamento.iloc[0].get('data_retorno', np.nan)):
                return 0
        
        # Verificar status em ATIVOS.xlsx
        if not self.planilhas['ativos'].empty:
            ativo = self.planilhas['ativos'][self.planilhas['ativos']['matricula'] == matricula]
            if not ativo.empty:
                status = ativo.iloc[0].get('desc.situacao', '')
                if status not in ['Trabalhando', 'Férias']:
                    # Verificar se não está na planilha de afastamentos
                    if self.planilhas['afastamentos'].empty or \
                       matricula not in self.planilhas['afastamentos']['matricula'].values:
                        return 0
        
        # Verificar desligamentos
        if not self.planilhas['desligamentos'].empty:
            desligamento = self.planilhas['desligamentos'][
                self.planilhas['desligamentos']['matricula'] == matricula
            ]
            if not desligamento.empty:
                data_comunicacao = pd.to_datetime(desligamento.iloc[0]['data_comunicacao'])
                data_demissao = pd.to_datetime(desligamento.iloc[0]['data_demissao'])
                
                # Se comunicado antes do dia 15/04, dias úteis = 0
                if data_comunicacao < self.inicio_competencia:
                    return 0
                
                # Se comunicado depois do dia 15/04, calcular até a data de demissão
                fim_calculo = min(data_demissao, self.fim_competencia)
                return self.contar_dias_uteis(self.inicio_competencia, fim_calculo, estado)
        
        # Verificar exterior
        if not self.planilhas['exterior'].empty:
            exterior = self.planilhas['exterior'][self.planilhas['exterior']['matricula'] == matricula]
            if not exterior.empty:
                data_retorno = exterior.iloc[0].get('data_retorno')
                if pd.isna(data_retorno):
                    return 0
                else:
                    data_retorno = pd.to_datetime(data_retorno)
                    if data_retorno > self.fim_competencia:
                        return 0
                    inicio_calculo = max(data_retorno, self.inicio_competencia)
                    return self.contar_dias_uteis(inicio_calculo, self.fim_competencia, estado)
        
        # Calcular para admissões em abril
        if data_admissao:
            data_admissao = pd.to_datetime(data_admissao)
            if data_admissao > self.inicio_competencia:
                # Admissão posterior ao início do período
                inicio_calculo = data_admissao
            else:
                # Admissão anterior ao período
                inicio_calculo = self.inicio_competencia
            
            dias_base = self.contar_dias_uteis(inicio_calculo, self.fim_competencia, estado)
        else:
            # Calcular para o período completo
            dias_base = self.contar_dias_uteis(self.inicio_competencia, self.fim_competencia, estado)
        
        # Descontar dias de férias
        if not self.planilhas['ferias'].empty:
            ferias = self.planilhas['ferias'][self.planilhas['ferias']['matricula'] == matricula]
            if not ferias.empty:
                for _, ferias_row in ferias.iterrows():
                    dias_ferias = int(ferias_row.get('dias_ferias', 0))
                    dias_base = max(0, dias_base - dias_ferias)
        
        return max(0, dias_base)
    
    def obter_valor_vr_sindicato(self, sindicato):
        """Obtém o valor do VR para o sindicato"""
        # Primeiro tenta buscar na planilha VR MENSAL
        if not self.planilhas['vr_mensal'].empty:
            vr_sindicato = self.planilhas['vr_mensal'][
                self.planilhas['vr_mensal']['sindicato'] == sindicato
            ]
            if not vr_sindicato.empty:
                return float(vr_sindicato.iloc[0].get('valor_diario_vr', 0))
        
        # Se não encontrar, usar valores padrão
        return self.valores_vr_sindicato.get(sindicato, 30.00)  # Valor padrão
    
    def processar_calculos(self):
        """Processa todos os cálculos e gera o resultado final"""
        resultado = []
        
        # Coletar todas as matrículas únicas de todas as planilhas
        todas_matriculas = set()
        
        for nome, df in self.planilhas.items():
            if not df.empty and 'matricula' in df.columns:
                todas_matriculas.update(df['matricula'].dropna().astype(str))
        
        print(f"Processando {len(todas_matriculas)} matrículas únicas...")
        
        for i, matricula in enumerate(sorted(todas_matriculas), 1):
            if i % 100 == 0:
                print(f"Processadas {i} matrículas...")
            
            # Buscar informações da matrícula
            data_admissao = None
            sindicato = None
            
            # Procurar nas planilhas por informações da matrícula
            for nome, df in self.planilhas.items():
                if not df.empty and 'matricula' in df.columns:
                    info_matricula = df[df['matricula'].astype(str) == str(matricula)]
                    if not info_matricula.empty:
                        row = info_matricula.iloc[0]
                        if 'data_admissao' in row and pd.notna(row['data_admissao']) and not data_admissao:
                            data_admissao = row['data_admissao']
                        if 'sindicato' in row and pd.notna(row['sindicato']) and not sindicato:
                            sindicato = row['sindicato']
            
            # Calcular dias úteis
            dias_uteis = self.calcular_dias_uteis_matricula(matricula, data_admissao, sindicato)
            
            # Obter valor diário VR
            valor_diario_vr = self.obter_valor_vr_sindicato(sindicato) if sindicato else 30.00
            
            # Calcular totais
            total = valor_diario_vr * dias_uteis
            custo_empresa = total * 0.8
            desconto_profissional = total * 0.2
            
            resultado.append({
                'Matrícula': matricula,
                'Admissão': data_admissao,
                'Sindicato': sindicato,
                'Competência': '05/2025',
                'Dias': dias_uteis,
                'VALOR DIÁRIO VR': valor_diario_vr,
                'TOTAL': total,
                'Custo empresa': custo_empresa,
                'Desconto profissional': desconto_profissional
            })
        
        return pd.DataFrame(resultado)
    
    def salvar_resultado(self, df_resultado, nome_arquivo='VR MENSAL RESULTADO.xlsx'):
        """Salva o resultado final em Excel"""
        try:
            df_resultado.to_excel(nome_arquivo, index=False)
            print(f"✓ Resultado salvo em: {nome_arquivo}")
            print(f"Total de registros: {len(df_resultado)}")
            print(f"Total geral VR: R$ {df_resultado['TOTAL'].sum():,.2f}")
            print(f"Total custo empresa: R$ {df_resultado['Custo empresa'].sum():,.2f}")
            print(f"Total desconto profissional: R$ {df_resultado['Desconto profissional'].sum():,.2f}")
        except Exception as e:
            print(f"❌ Erro ao salvar resultado: {str(e)}")

def main():
    """Função principal para executar o cálculo de VR"""
    print("=== CALCULADORA DE VALE REFEIÇÃO ===")
    print(f"Período de competência: 15/04/2025 à 15/05/2025")
    print("=" * 50)
    
    # Criar instância do calculador
    calc = VRCalculator()
    
    # Carregar planilhas
    print("\n1. Carregando planilhas...")
    calc.carregar_planilhas()
    
    # Processar cálculos
    print("\n2. Processando cálculos...")
    resultado = calc.processar_calculos()
    
    # Exibir resumo
    print("\n3. Resumo dos resultados:")
    print(f"   - Total de matrículas processadas: {len(resultado)}")
    print(f"   - Matrículas com dias úteis > 0: {len(resultado[resultado['Dias'] > 0])}")
    print(f"   - Total geral VR: R$ {resultado['TOTAL'].sum():,.2f}")
    
    # Salvar resultado
    print("\n4. Salvando resultado...")
    calc.salvar_resultado(resultado)
    
    print("\n✓ Processamento concluído!")
    return resultado

# Executar se o script for chamado diretamente
if __name__ == "__main__":
    resultado = main()
    
    # Exibir primeiras linhas do resultado
    print("\nPrimeiras 10 linhas do resultado:")
    print(resultado.head(10).to_string(index=False))