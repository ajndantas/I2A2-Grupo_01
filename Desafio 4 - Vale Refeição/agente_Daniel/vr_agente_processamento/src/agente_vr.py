"""
AGENTE INTELIGENTE DE PROCESSAMENTO DE VR
Versão completa com todos os sindicatos identificados
"""

import pandas as pd
from typing import Dict, Tuple
import agente_dias_uteis

class AgenteVR:
    def __init__(self):
        """Inicializa o agente com as regras de negócio"""
        
        data_inicio_mes_competencia = '2025-04-15'
        data_fim_mes_competencia = '2025-05-15'
        dictintervalo_competencia = {"data_inicio_mes_competencia" : data_inicio_mes_competencia, "data_fim_mes_competencia" : data_fim_mes_competencia}
        
        uploaded_file_base_dias = "Base dias uteis.xlsx"
        
        qtd_dias_uteis = agente_dias_uteis.main(uploaded_file_base_dias, dictintervalo_competencia)
        
        for d in qtd_dias_uteis:
            
            if d['estado'] == 'SP':
                dias_uteis_sp = d['qtd_dias_uteis']
                
            elif d['estado'] == 'RJ':
                dias_uteis_rj = d['qtd_dias_uteis']
                
            elif d['estado'] == 'RS':
                dias_uteis_rs = d['qtd_dias_uteis']
                
            elif d['estado'] == 'PR':
                dias_uteis_pr = d['qtd_dias_uteis']
                  
        # MAPEAMENTO CORRETO baseado nos dados reais
        self.regras_sindicato = {            
            
            'SINDPD SP - SIND.TRAB.EM PROC DADOS E EMPR.EMPRESAS PROC DADOS ESTADO DE SP.': {
                'estado': 'SP',
                'valor_diario': 37.50,
                'dias_uteis': dias_uteis_sp
            },
            'SINDPPD RS - SINDICATO DOS TRAB. EM PROC. DE DADOS RIO GRANDE DO SUL': {
                'estado': 'RS',
                'valor_diario': 35.00,
                'dias_uteis': dias_uteis_rs
            },
            'SITEPD PR - SIND DOS TRAB EM EMPR PRIVADAS DE PROC DE DADOS DE CURITIBA E REGIAO METROPOLITANA': {
                'estado': 'PR',
                'valor_diario': 35.00,
                'dias_uteis': dias_uteis_pr
            },
            'SINDPD RJ - SINDICATO PROFISSIONAIS DE PROC DADOS DO RIO DE JANEIRO': {
                'estado': 'RJ',
                'valor_diario': 35.00,  # Confirmar este valor
                'dias_uteis': dias_uteis_rj
            }
        }
        
        # Lista de matrículas para excluir (será preenchida)
        self.matriculas_excluir = set()
        
        # Log de decisões do agente
        self.log_decisoes = []
        
        print("Agente VR inicializado!")
        print(f"Conheço {len(self.regras_sindicato)} sindicatos")
        print(f"Total de funcionários esperado: ~1815")
    
    def carregar_exclusoes(self, caminho_dados):
        """Carrega todas as listas de exclusão"""
        contador_exclusoes = 0
        
        # Carregar APRENDIZES
        try:
            df_aprendiz = pd.read_excel(f"{caminho_dados}/APRENDIZ.xlsx")
            aprendizes = set(df_aprendiz['MATRICULA'].astype(str))
            self.matriculas_excluir.update(aprendizes)
            contador_exclusoes += len(aprendizes)
            print(f"  Carregou {len(aprendizes)} aprendizes para exclusão")
        except Exception as e:
            print(f"  Aviso: Erro ao carregar aprendizes: {e}")
        
        # Carregar ESTAGIÁRIOS
        try:
            df_estagio = pd.read_excel(f"{caminho_dados}/ESTÁGIO.xlsx")
            estagiarios = set(df_estagio['MATRICULA'].astype(str))
            self.matriculas_excluir.update(estagiarios)
            contador_exclusoes += len(estagiarios)
            print(f"  Carregou {len(estagiarios)} estagiários para exclusão")
        except Exception as e:
            print(f"  Aviso: Erro ao carregar estagiários: {e}")
        
        # Carregar AFASTAMENTOS
        try:
            df_afastamentos = pd.read_excel(f"{caminho_dados}/AFASTAMENTOS.xlsx")
            afastados = set(df_afastamentos['MATRICULA'].astype(str))
            self.matriculas_excluir.update(afastados)
            contador_exclusoes += len(afastados)
            print(f"  Carregou {len(afastados)} afastados para exclusão")
        except Exception as e:
            print(f"  Aviso: Erro ao carregar afastamentos: {e}")
        
        # Carregar EXTERIOR
        try:
            df_exterior = pd.read_excel(f"{caminho_dados}/EXTERIOR.xlsx")
            # Cuidado: coluna pode ter nome diferente
            if 'Cadastro' in df_exterior.columns:
                exterior = set(df_exterior['Cadastro'].astype(str))
            else:
                exterior = set(df_exterior.iloc[:,0].astype(str))
            self.matriculas_excluir.update(exterior)
            contador_exclusoes += len(exterior)
            print(f"  Carregou {len(exterior)} no exterior para exclusão")
        except Exception as e:
            print(f"  Aviso: Erro ao carregar exterior: {e}")
        
        print(f"Total de matrículas marcadas para exclusão: {len(self.matriculas_excluir)}")
        return self.matriculas_excluir
    
    def decidir_elegibilidade(self, funcionario: Dict) -> Tuple[bool, str]:
        """
        Decide se um funcionário é elegível para VR
        Retorna: (elegível: bool, motivo: str)
        """
        matricula = str(funcionario.get('MATRICULA', ''))
        cargo = funcionario.get('TITULO DO CARGO', '')
        
        # Verificar se está na lista de exclusão
        if matricula in self.matriculas_excluir:
            return False, "Matrícula na lista de exclusão"
        
        # Verificar se é diretor
        if cargo and 'DIRETOR' in cargo.upper():
            return False, "Cargo de Diretor"
        
        return True, "Elegível"
    
    def calcular_valor_vr(self, sindicato: str, dias_trabalhados: int) -> Dict:
        """Calcula o valor do VR baseado no sindicato e dias"""
        
        # Buscar regras do sindicato
        regras = self.regras_sindicato.get(sindicato)
        
        if not regras:
            print(f"Aviso: Sindicato não mapeado: {sindicato}")
            return None
        
        valor_diario = regras['valor_diario']
        valor_total = dias_trabalhados * valor_diario
        
        return {
            'valor_diario': valor_diario,
            'dias': dias_trabalhados,
            'total': valor_total,
            'custo_empresa': round(valor_total * 0.8, 2),
            'desconto_funcionario': round(valor_total * 0.2, 2)
        }
    
    def processar_desligamentos(self, caminho_dados):
        """Processa regras de desligamento"""
        try:
            df_desligados = pd.read_excel(f"{caminho_dados}/DESLIGADOS.xlsx")
            
            # Desligados com OK até dia 15 devem ser excluídos
            for _, row in df_desligados.iterrows():
                if row.get('COMUNICADO DE DESLIGAMENTO') == 'OK':
                    # Verificar se data é até dia 15
                    # Como a data está em formato numérico Excel, precisamos converter
                    matricula = str(row['MATRICULA '])  # Note o espaço após MATRICULA
                    self.matriculas_excluir.add(matricula)
                    self.log_decisoes.append(f"Matrícula {matricula}: Desligado com OK - excluído")
            
            print(f"  Processou {len(df_desligados)} desligamentos")
        except Exception as e:
            print(f"  Erro ao processar desligamentos: {e}")
    
    def gerar_relatorio(self):
        """Gera relatório das decisões do agente"""
        print("\n" + "="*60)
        print("RELATÓRIO DO AGENTE")
        print("="*60)
        print(f"Total de exclusões identificadas: {len(self.matriculas_excluir)}")
        print(f"Decisões registradas: {len(self.log_decisoes)}")
        
        if self.log_decisoes:
            print("\nÚltimas 10 decisões:")
            for decisao in self.log_decisoes[-10:]:
                print(f"  {decisao}")