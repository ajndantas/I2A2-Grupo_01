# [markdown]
# # <center><b>Desafio 3 - Titanic - Aprendizado de Máquina a partir do Desastre</b></center>

# [markdown]
# ## <b>ARQUIVOS e DATAFRAMES</b>
# <ul>
#     <li>train.csv -> Será usado para construir o modelo de aprendizado de máquina <br/>
#     <li>test.csv -> Será usado para testar o modelo
# </ul>

# [markdown]
# https://www.kaggle.com/competitions/titanic<br/><br/>
# Data Cleaning Process -> https://www.youtube.com/watch?v=Y_s3hndYbB0&t=49s<br/>
# EDA -> https://youtu.be/xLW796-J5fI?is=PnHRjUx7owx_0BFc

from pandas import read_csv

train = 'https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%203/titanic/train.csv'
test = 'https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%203/titanic/test.csv'

df_train = read_csv(train)
df_test = read_csv(test)

# [markdown]
# ## <center><b>DATAFRAME DE TREINAMENTO</b></center>

# [markdown]
# ## <b>ANÁLISE DOS DADOS</b>

df_train.head(10)

df_train.tail(10)

# [markdown]
# ## <b>DATA CLEANING</b>

# [markdown]
# <ul>
#     <li><b>Detectando valores faltantes, tipos de dados, quantidade de linhas e colunas</b></li>
#     <li><b>Normalizando os nomes das colunas</b></li>
#     <li><b>Porcentagem de valores nulos</b></li>
#     <li><b>Lidando com duplicatas, valores nulos e colunas bagunçadas (Padronizar colunas com valores categóricos)</b></li>
#     <li><b>Modificando nomes de colunas</b></li>
#     <li><b>Criação de novas variáveis para substituir outras de menor relevância</b></li>
#     <li><b>Eliminando variáveis desnecessárias</b></li>    
# </ul>

# [markdown]
# <b>Detectando valores faltantes, tipos de dados, quantidade de linhas e colunas</b>

df_train.info()

# [markdown]
# <b>Normalizando os nomes das colunas</b>
# <ul>
#     <li>Colocando tudo como minúscula</li>
#     <li>Removendo espaços em branco</li>
#     <li>Removendo parenteses (Não será necessário)</li>
# </ul>

df_train.columns = (
                        df_train.columns.
                        str.lower().
                        str.strip().
                        str.replace(' ','_')
                    )

df_train.columns



# [markdown]
# <b>Porcentagem de valores nulos</b>

# [markdown]
# Se os dados tiverem mais do que 40% de valores nulos, eles devem ser checados/descartados

missing = ((df_train.isnull().sum() / len(df_train)) * 100)
missing[missing>0]

# [markdown]
# Descartando a coluna 'cabin'

df_train = df_train.drop(columns='cabin',axis=1,errors='ignore')
df_train

# [markdown]
# <b>Lidando com duplicatas, valores nulos e colunas bagunçadas (Padronizar colunas com valores categóricos)</b>

# [markdown]
# <ul>
#     <li>Cheque a quantidade de duplicatas antes de remover. Para remover, use df.drop_duplicates()</li>
#     <li>Os valores nulos de colunas de valores numéricos, devem ser preenchidos com a média da coluna</li>
#     <li>Os valores nulos de colunas categóricas, devem ser preenchidas como "desconhecido"</li>
#     <li>'Capitalize' colunas com valores categóricos (Não é o caso deste dataframe)</li>
#     <li>Retirar símbolo de moedas de colunas com valores monetários, vírgulas ou pontos.</li>    
#     <li>Usar map para colunas de datas aonde alguns valores possuem "-", em vez de "/", formatação numérica (Não é o caso deste dataframe)</li>
#     <li>Usar map para colunas de diferentes valores booleanos como Yes, No, 1,0, etc... para true ou false. Exemplo abaixo. (Não é o caso deste dataset)
#     <img src="boolean_substitutions.jpg"/>
#     </li>
#     <li>Usar map para normalizar valores de colunas que possuem nomes de países. Exemplo abaixo! (Não é o caso deste dataset) <img src="image.png"/>   
#     </li>
#     <li>Desconfie de colunas do tipo object</li>
#     <li>Utilize a lógica para outros tipos de colunas. Ex: coluna de quantidade com valores negativos</li>
# </ul>

# [markdown]
# Cheque a quantidade de duplicatas antes de remover. Para remover, use df.drop_duplicates()

df_train.duplicated().sum()

# [markdown]
# Os valores nulos de colunas de valores numéricos, devem ser preenchidos com a média da coluna

missing = df_train.isnull().sum()
missing[missing>0]

# [markdown]
# Os valores nulos de colunas categóricas, devem ser preenchidas como "desconhecido

df_copy = df_train.copy()

df_train['age'] = df_train['age'].fillna(df_train['age'].mean())
df_train['age'] = df_train['age'].astype(int) # Ocorre truncagem
df_train['embarked'] = df_train['embarked'].fillna('Unknown')
df_train

# [markdown]
# Padronizando algumas colunas

from pandas import to_numeric


df_train['sex'] = (
                    df_train['sex'].
                    str.lower().
                    str.strip()
                  )

df_train

# [markdown]
# Retirar símbolo de moedas de colunas com valores monetários, vírgulas ou pontos.

df_train['fare'] = (
                      df_train['fare'].
                      astype(str).replace('$','').
                      str.replace(',','.').
                      str.strip()
                    ) 

df_train['fare'] = to_numeric(df_train['fare'],errors='coerce') # errors='coerce' ignora os erros
df_train


# [markdown]
# Desconfie de colunas do tipo object - Ticket é aleatória

df_train.info()

df_train['name'] = (
                    df_train['name'].
                    str.strip().
                    str.capitalize()
                  )

print('Busca por linhas que contenham somente números nas colunas abaixo:')
for col in ['name','sex','embarked']:
    print("Coluna: ",col, " - Qtd: " ,df_train[col].str.isdigit().sum())

# [markdown]
# <b>Modificando nomes de colunas</b>

df_train.rename(columns={'pclass':'passenger_class','parch':'parents_children','sibsp':'siblings'},inplace=True)
df_train

# [markdown]
# <b>Criação de novas variáveis para substituir outras de menor relevância</b>

# [markdown]
# <ul>
#     <li>family_size = parents_children + siblings</li>
# </ul>

df_train['family_size'] = df_train['parents_children'] + df_train['siblings']
df_train = df_train.drop(columns=['parents_children', 'siblings'], axis=1)
df_train

# [markdown]
# <b>Eliminando variáveis desnecessárias</b>

df_train.columns

df_train = df_train.drop(columns=['ticket','fare','embarked'],errors='ignore')
df_train

# [markdown]
# Criando o novo arquivo de treinamento

df_train.to_csv('train.csv',index=False)

# [markdown]
# ## <center><b>DATAFRAME DE TESTE</b></center>

# [markdown]
# ## <b>ANÁLISE DOS DADOS</b>

df_test.head(10)

df_test.tail(10)

# [markdown]
# ## <b>DATA CLEANING</b>

# [markdown]
# <b>Detectando valores faltantes, tipos de dados, quantidade de linhas e colunas</b>

df_test.info()

# [markdown]
# <b>Normalizando os nomes das colunas</b>

df_test.columns = (
                    df_test.columns.
                    str.strip().
                    str.lower().
                    str.replace(' ','_')
                 )
df_test.columns

# [markdown]
# <b>Porcentagem de valores nulos</b>

missing = df_test.isnull().sum()
missing = missing[missing>0]
missing

percentage = ((missing / len(df_test)) * 100).round(2)
percentage

# [markdown]
# Desprezando a coluna cabin, pois ela possui muitos valores nulos

df_test = df_test.drop(columns=['cabin'],errors='ignore')
df_test

# [markdown]
# <b>Lidando com duplicatas, valores nulos e colunas bagunçadas (Padronizar colunas com valores categóricos)</b>

# [markdown]
# Cheque a quantidade de duplicatas antes de remover.

df_test.duplicated().sum()

# [markdown]
# Os valores nulos de colunas de valores numéricos, devem ser preenchidos com a média da coluna

# age, fare
df_test['age'] = df_test['age'].fillna(df_test['age'].mean())
df_test['age'] = df_test['age'].astype(int)
df_test['fare'] = df_test['fare'].fillna(df_test['fare'].mean())
df_test

# [markdown]
# Retirar símbolo de moedas de colunas com valores monetários, vírgulas ou pontos.

df_test['fare'] = (
                      df_test['fare'].
                      round(2).
                      astype(str).
                      replace('$','').
                      str.replace(',','.').
                      str.strip()
                   )

df_test['fare'] = to_numeric(df_test['fare'],errors='coerce')
df_test

# [markdown]
# Desconfie de colunas do tipo object - Ticket é aleatória

df_test.info()

df_test['name'] = (
                    df_test['name'].
                    str.strip().
                    str.capitalize()
                  )

print('Busca por linhas que contenham somente números nas colunas abaixo:')
for col in ['name','sex','embarked']:
    print("Coluna: ",col, " - Qtd: " ,df_test[col].str.isdigit().sum())

# [markdown]
# <b>Modificando nomes de colunas</b>

df_test.rename(columns={'pclass':'passenger_class','parch':'parents_children','sibsp':'siblings'},inplace=True)
df_test

# [markdown]
# <b>Criação de novas variáveis para substituir outras de menor relevância</b>

# [markdown]
# <ul>
#     <li>family_size = parents_children + siblings + 1 (Por causa do valor 0)</li>
# </ul>

df_test['family_size'] = df_test['parents_children'] + df_test['siblings']
df_test = df_test.drop(columns=['parents_children', 'siblings'], axis=1)
df_test

# [markdown]
# <b>Eliminando variáveis desnecessárias</b>

df_test.columns

df_test = df_test.drop(columns=['ticket','fare','embarked'],errors='ignore')
df_test

# [markdown]
# Criando o novo arquivo de teste

df_test.to_csv('test.csv',index=False)

# [markdown]
# ## <center><b>ANÁLISE EXPLORATÓRIA NO DATAFRAME DE TREINAMENTO</b></center>

df_train.describe()

# [markdown]
# <b>A variável alvo é a sobrevivência</b>

# [markdown]
# <b>Conceitos</b>

# [markdown]
# <ul>
#     <li><b>Tendência Central (Média, Mediana e Moda) - Moda:</b> Ocorrência mais frequente</li>
#     <li><b>Tendência Central (Média, Mediana e Moda) - Mediana:</b> A Mediana é literalmente o valor do meio de um conjunto de dados. Para encontrá-la, você obrigatoriamente precisa colocar os dados em ordem (do menor para o maior). Ela divide os seus dados exatamente na metade: 50% dos valores estão abaixo da mediana e 50% estão acima. A vantegem dela é que é imune a valores extremos<br/><br/>
#     <ul>
#         <li>Se a quantidade de dados for ímpar: A mediana é o número que está exatamente no centro.</li>
#         <li>Se a quantidade de dados for par: A mediana é a média dos dois números centrais.</li>
#         <li><img src="mediana.jpg"/></li>
#         <li>1. Curva Simétrica (Média = Mediana = Moda): Os dados são perfeitamente balanceados.</li>
#         <li>2. Assimetria Positiva (Média > Mediana > Moda): Os dados estão concentrados nos valores baixos, mas existem poucos valores absurdamente altos que puxam a média para cima.</li>
#         <li>3. Assimetria Negativa (Média > Mediana > Moda): Os dados estão concentrados nos valores baixos, mas existem poucos valores absurdamente altos que puxam a média para cima.</li>
#     </ul>
#     <li><b>Dispersão - Variância: Mede o quadrado da distância média de cada ponto em relação à média</b> </li>
#     <li><b>Dispersão - Desvio Padrão: Raíz quadrada da variância</b> </li>
#     <li><b>Distribuição - Histogramas ou gráficos de barras ou porcentagem: </b>Os comportamentos 1, 2 e 3 são expressos por histogramas ou gráficos de barras com porcentagem.</li>
#     <li><b>Associação - Correlação:</b> A correlação (especificamente o coeficiente de Pearson) indica a força e a direção da relação linear entre duas variáveis. Ela varia estritamente entre -1 e 1</li>
#     <li><b>Correlação + Desvio Padrão (Gestão de Riscos / Investimentos): </b>Se você analisa duas variáveis que têm forte correlação positiva, mas ambas possuem um desvio padrão elevadíssimo, você conclui que, embora elas caminhem juntas, a jornada será de altíssima volatilidade e risco. No mercado financeiro, busca-se ativos com correlação negativa ou nula para balancear carteiras e reduzir o desvio padrão (risco) global do portfólio.</li>
# </ul>
#

# [markdown]
# <b>Contagem de sobreviventes e não sobreviventes</b>

# Exemplo 1 - Gráfico de barras simples
import matplotlib.pyplot as plt

survived = df_train.loc[df_train['survived'] == 1]['survived'].count()
not_survived = df_train.loc[df_train['survived'] == 0]['survived'].count()
total = survived + not_survived

data = {'sobreviventes': survived, 'não_sobreviventes': not_survived}
names = list(data.keys())
values = list(data.values())

fig, axs = plt.subplots(figsize=(9, 3)) # A função subplot cria uma figura e um ou mais eixos.
                                        # O parâmetro figsize define o tamanho da figura. 9 é a largura e 3 é a altura.

colors = ['#1f77b4', '#e74c3c']
bars = axs.bar(names, values, color=colors)

# 2. Adicionando a porcentagem (e o valor absoluto) no topo das barras
labels = [f'{v} ({v/total*100:.1f}%)' for v in values]
axs.bar_label(bars, labels=labels, padding=3)

# Ajustando o limite do eixo Y para o texto não cortar no topo
axs.set_ylim(0, max(values) * 1.15)

fig.suptitle('Sobreviventes / Não Sobreviventes')  
plt.show()

# [markdown]
# <b>Taxa de sobrevivência x Sexo</b>

df_survived_sex = df_train.groupby('sex').agg(
                                                total=('survived', 'count'), total_survived=('survived', 'sum')
                                            ).reset_index() 

df_survived_sex['percentage'] = ((df_survived_sex['total_survived'] / df_survived_sex['total']) * 100).round(2)

df_survived_sex

# Exemplo 1 - Gráfico de barras simples
import matplotlib.pyplot as plt
data = {'sexo': df_survived_sex['sex'].to_list(), 'Taxa de sobrevivência': df_survived_sex['percentage'].to_list()}

bars = plt.bar(data['sexo'], data['Taxa de sobrevivência'],color=["#a81fb4",'#1f77b4'])

# Adicionando os rótulos no topo das barras
plt.bar_label(bars, fmt='%.1f%%', padding=1) # fmt='%.1f%%': É o formatador do texto.
                                             # %.1f significa que o número será exibido como um ponto flutuante (float) com uma casa decimal (ex: 45.2).
                                             # %% -> É a forma de dizer ao Python para colocar o caractere literal de porcentagem (%) no final do texto.

# Configuração do eixo x
plt.xlabel('Sexo')
plt.ylabel('Taxa de Sobrevivência(%)')
plt.title('Taxa de Sobrevivência x Sexo')
 
plt.show()



# [markdown]
# <b>Taxa de sobrevivência x Idades</b>

# [markdown]
# <ul>
#     <li>Para calcular a taxa de sobrevivência por faixa etária no seu script, a melhor abordagem é agrupar os dados contínuos de idade em intervalos (bins) usando a função pd.cut() do Pandas.</li><br/>
#     <li>Trabalhar com idades individuais (0, 1, 2, ..., 80 anos) costuma gerar um gráfico "poluído" e com ruído, enquanto a criação de faixas etárias (ex: Criancas, Jovens, Adultos, Idosos) permite identificar padrões claros de sobrevivência.</li>
# </ul>

from pandas import cut

# 1. Definir os limites dos intervalos e os rótulos de cada faixa etária
bins = [0, 12, 18, 35, 60, 100]
labels = ['Crianças (0-12)', 'Adolescentes (13-18)', 'Jovens Adultos (19-35)', 'Adultos (36-60)', 'Idosos (60+)']

# 2. Criar uma nova coluna temporária com a faixa etária
df_train['faixa_etaria'] = cut(df_train['age'], bins=bins, labels=labels)

# Definindo como categoria
df_train['faixa_etaria'] = df_train['faixa_etaria'].astype('category')
df_train

# 3. Calcular o total de pessoas e os sobreviventes por faixa etária
df_faixas = df_train.groupby('faixa_etaria', observed=False).agg(
    total=('survived', 'count'),
    sobreviventes=('survived', 'sum')
).reset_index()

# 4. Calcular a taxa de sobrevivência (%)
df_faixas['taxa_sobrevivencia'] = ((df_faixas['sobreviventes'] / df_faixas['total']) * 100).round(2)

df_faixas

import numpy as np
import matplotlib.pyplot as plt

# 5. Plotar o gráfico de barras
plt.figure(figsize=(10, 5))
bars = plt.bar(df_faixas['faixa_etaria'], df_faixas['taxa_sobrevivencia'], color='#1f77b4')

# Adicionar os rótulos de porcentagem no topo de cada barra
plt.bar_label(bars, fmt='%.1f%%', padding=3)

plt.xlabel('Faixa Etária')
plt.ylabel('Taxa de Sobrevivência (%)')

plt.title('Taxa de Sobrevivência x Faixa Etária')
plt.ylim(0, max(df_faixas['taxa_sobrevivencia']) * 1.15)

plt.xticks(rotation=15) # O rotation representa a inclinação dos rótulos no eixo

# Calculando a linha de tendência (Regressão Linear)
# O número 1 indica que queremos uma linha reta (polinômio de grau 1)
# O que faz p np.polyfit e o polyid ?
df_faixas['faixa_etaria'] = df_faixas['faixa_etaria'].astype('category') # Convertendo para poder ser usado na plotagem do gráfico

coeficientes = np.polyfit(df_faixas['faixa_etaria'].cat.codes, df_faixas['taxa_sobrevivencia'],2) # Calcula a matemática por trás da curva, 
funcao_tendencia = np.poly1d(coeficientes) # e o np.poly1d transforma essa matemática em uma função prática que você pode usar para desenhar a linha ou prever valores.

# 3. Plotando a linha de tendência
plt.plot(df_faixas['faixa_etaria'], funcao_tendencia(df_faixas['faixa_etaria'].cat.codes), 
         color='red', linestyle='-', linewidth=2, label='Tendência')

plt.tight_layout() # O tight_layout ajusta automaticamente os elementos no gráfico

# [markdown]
# Concluímos que taxa de sobrevivência veio diminuindo com o avanço da idade.

# [markdown]
# <b>Taxa de Sobrevivência x Classe do Passageiro</b>

df_survived_class = df_train.groupby('passenger_class').agg(total=('survived', 'count'), total_survived=('survived', 'sum')).reset_index()
df_survived_class['percentage'] = ((df_survived_class['total_survived'] / df_survived_class['total']) * 100).round(2)
df_survived_class

data = {'classes': df_survived_class['passenger_class'].to_list(), 'Taxa de sobrevivência': df_survived_class['percentage'].to_list()}

bars = plt.bar(data['classes'], data['Taxa de sobrevivência'], color='#1f77b4')


# Adicionando os rótulos no topo das barras
# O parâmetro fmt='%.1f%%' formata o número com uma casa decimal e o símbolo de %
plt.bar_label(bars, fmt='%.1f%%', padding=1) 

plt.xticks(df_survived_class['passenger_class'])
plt.xlabel('Classe do Passageiro')
plt.ylabel('Taxa de Sobrevivência(%)')
plt.title('Taxa de Sobrevivência x Classe do Passageiro')
 
plt.show()


# [markdown]
# Concluímos que a taxa de sobrevivencia diminui nas classes 2 e 3 e aumenta na classe 1

# [markdown]
# <b>Taxa de Sobrevivencia x Tamanho da Família (Pais, filhos e parentes)</b>

df_family_size = df_train[['family_size']]
df_family_size = df_family_size.groupby(['family_size']).agg(total=('family_size','count')).reset_index()

df_family_size

df_survived_familysize = df_train.loc[df_train['survived'] == 1].groupby(['family_size']).agg(total=('family_size','count')).reset_index()
df_survived_familysize['percentage'] = ((df_survived_familysize['total'] / df_family_size['total']) * 100).round(2)

df_survived_familysize

data = {'tamanho': df_survived_familysize['family_size'].to_list(), 'Taxa de sobrevivência': df_survived_familysize['percentage'].to_list()}

bars = plt.bar(data['tamanho'], data['Taxa de sobrevivência'])

plt.bar_label(bars, fmt='%.1f%%', padding=1) 

# 2. Calculando a linha de tendência (Regressão Linear)
# O número 1 indica que queremos uma linha reta (polinômio de grau 1)
coeficientes = np.polyfit(df_survived_familysize['family_size'], df_survived_familysize['percentage'], 2) 
funcao_tendencia = np.poly1d(coeficientes)

# 3. Plotando a linha de tendência
plt.plot(df_survived_familysize['family_size'], funcao_tendencia(df_survived_familysize['family_size']), 
         color='red', linestyle='-', linewidth=2, label='Tendência')

plt.xlabel('Tamanho da Família')
plt.ylabel('Taxa de Sobrevivência(%)')
plt.title('Taxa de Sobrevivência x Tamanho da Família')
plt.show()

# [markdown]
# Concluímos que a taxa de sobrevivencia aumenta para uma família até 3 pessoas e diminui a partir daí

# [markdown]
# <b>Correlação</b>

# 1. Carregar o arquivo no DataFrame df_train

# 2. Calcular a matriz de correlação (apenas para colunas numéricas)
df_correlacao = df_train.drop(columns='passengerid').corr(numeric_only=True).round(2)

# Exibir a matriz no terminal
df_correlacao

# Criar gráfico de calor (Heatmap)
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 6))
sns.heatmap(df_correlacao, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5) # 2. annot=True (Annotation / Anotação. 
                                                                                   # O que faz: Exibe o valor numérico dentro de cada célula da matriz.
                                                                                   #
                                                                                   # 3. cmap='coolwarm' (Color Map / Paleta de Cores)
                                                                                   # O que faz: Define o esquema ou gradiente de cores usado para representar 
                                                                                   # a variação dos dados.
                                                                                   #
                                                                                   # 4. fmt=".2f" (Formatting / Formatação de Texto)
                                                                                   # O que faz: Controla a formatação de exibição dos números ativados pelo 
                                                                                   # annot=True usando a sintaxe de formatação do Python.
                                                                                   # O que significa ".2f":
                                                                                   # .2 = Exibe exatamente 2 casas decimais, f = Trata o número como ponto flutuante.
                                                                                   #
                                                                                   # 5. linewidths=0.5 (Linhas Divisórias)
                                                                                   # O que faz: Define a espessura das linhas brancas que separam cada célula do 
                                                                                   # mapa de calor.

plt.title('Matriz de Correlação - df_train')
plt.tight_layout() # O plt.tight_layout() inspeciona o tamanho do texto e dos eixos e ajusta as margens da figura (figure padding) 
                   # e o espaço entre eixos (subplot padding) para que tudo caiba perfeitamente.
plt.show()

# [markdown]
# <b>Conclusões da Correlação não ligadas as sobrevivência</b>
# <ul>
#     <li><b>Estrutura Familiar Integrada (siblings vs parents_children = +0.41):</b>Correlação positiva moderada. Passageiros que viajavam com irmãos/cônjuges (siblings) frequentemente também estavam acompanhados de pais/filhos (parents_children), indicando grupos familiares maiores a bordo.</li><br/>
#     <li><b>Idade e Classe (age vs passenger_class = -0.34):</b>Correlação negativa moderada. Passageiros mais velhos tendiam a ocupar classes superiores (1ª classe), enquanto os passageiros mais jovens estavam predominantemente na 3ª classe.</li><br/>
#     <li><b>age vs. family_size ( -0.25 ):</b> Relação negativa fraca a moderada. Contexto: Passageiros mais velhos tendiam a viajar sozinhos ou em casais (menor family_size), enquanto famílias com maior número de membros eram compostas por pais mais jovens e crianças.</li>
# <ul>

# [markdown]
# ## <center><b>APRENDIZADO DE MÁQUINA E PREVISÕES</b></center>

# [markdown]
# ## <center><b>Dataset de Teste</b></center>

# [markdown]
# #### <b>MODELO ESCOLHIDO COMO BASELINE</b>

# [markdown]
# O primeiro modelo escolhido foi o Linear SVC, por possuir características de ser um baseline rápido, com uma fronteira de decisão linear simples, antes de explorar interações complexas baseadas em árvore

# [markdown]
# <b>Etapas:</b>
#
# 1 - Carga dos Dados<br/>
# 2 - Definição das colunas<br/>
# 3 - Definição do Pipeline<br/>
# 4 - Definição do Modelo<br/>
# 5 - Acurácia<br/>
# 6 - Treinamento do Modelo<br/>
# 7 - Previsões

# [markdown]
# <b>Pré Requisitos para os dados</b>

# [markdown]
# <ul>
#     <li><b>Os dados numéricos, se possuirem grande variação, devem ser padronizados (Utilizar StandardScaler), pois a máquina associa que grandes valores têm maior peso na decisão</b></li><br/>
#     <li><b>Os dados categóricos devem ser transformados em dados numéricos (Isso pode ser feito por meio de OneHotEncoder), pois algoritmos de Álgebra linear são cegos para letras</b></li>
# </ul>

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC

# [markdown]
# <b>1 - Carga dos Dados</b>

# [markdown]
# <ul>
#     1 - Calculando a faixa etária para o dataframe test e eliminando a coluna age<br/>
#     2 - Eliminando a coluna age do dataframe train<br/>
# </ul>

# 1. Definir os limites dos intervalos e os rótulos de cada faixa etária
bins = [0, 12, 18, 35, 60, 100]
labels = ['Crianças (0-12)', 'Adolescentes (13-18)', 'Jovens Adultos (19-35)', 'Adultos (36-60)', 'Idosos (60+)']

# 2. Criando uma nova coluna com a faixa etária
df_test['faixa_etaria'] = cut(df_test['age'], bins=bins, labels=labels).astype('category')
df_test.drop(columns='age', errors='ignore', inplace=True)
df_test

df_train.drop(columns='age', errors='ignore', inplace=True)
df_train

# 1. Carga dos dados
train = df_train
test = df_test

X_train = train.drop(columns='survived') # axis=1, representa as colunas. Dados
y_train = train['survived'] # Classes


# [markdown]
# <b>2 - Definição das colunas</b>

# 2. Definição das colunas
num_cols = ['passenger_class', 'family_size']
cat_cols = ['sex','faixa_etaria']

# [markdown]
# <b>3 - Pipeline de Pré-processamento</b>

# [markdown]
# <ul>
#     <li><b>drop=first</b><br/><br/>
#     Ao definir drop='first', a primeira coluna one-hot é descartada, deixando apenas as colunas one-hot para os valores restantes. Isso é útil quando você deseja evitar a inclusão redundante de uma coluna que representa o valor original.
#
#     Por exemplo, se você tem uma coluna "sexo" com os valores "masculino" e "feminino", a codificação one-hot resultante terá duas colunas: "sexo_masculino" e "sexo_feminino". Se você não definir drop='first', terá três colunas: "sexo_masculino", "sexo_feminino" e "sexo" (que é igual ao valor original). Ao definir drop='first', você remove a coluna "sexo" redundante e mantém apenas "sexo_masculino" e "sexo_feminino".</li>
# </ul>

# 3. Pipeline de Pré-processamento
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), num_cols),
        ('cat', OneHotEncoder(drop='first'), cat_cols),
    ]
)


# [markdown]
# <b>4 - Modelo</b>

# [markdown]
# <ul>
#     <li><b>dual = False</b></li>
#     <li>Quando o número de passageiros, supera largamente o número de colunas, a otimização Primal é mais eficiente</li>   
# </ul>

# [markdown]
# ![image.png](attachment:image.png)

# [markdown]
# <ul>
#     <li><b>randon_state = 42</b><br/><br/>
#     No contexto de Aprendizado de Máquina (Machine Learning) e da biblioteca Scikit-Learn em Python, o parâmetro random_state = 42 é utilizado para definir a semente (seed) do gerador de números pseudoaleatórios.<br/><br/>
#     Muitos algoritmos envolvem processos aleatórios (como a divisão de dados em treino/teste, inicialização de pesos ou a criação de árvores em uma Random Forest), definir o random_state com um número fixo garante que toda vez que o código for executado, os dados serão divididos/gerados exatamente da mesma forma. Isso é crucial para:<br/><br/></li>
#     <ul>
#         <li>Comparar o desempenho de diferentes modelos sob as mesmas condições.</li>
#         <li>Permitir que outros colegas ou revisores executem o seu notebook e obtenham os mesmos resultados.</li>
#         <li>Por que o número 42 especificamente?<br/><br/>
#         A escolha do número 42 é uma convenção cultural / piada interna muito famosa no mundo da programação e ciência de dados.<br/>
#         Ele é uma referência direta ao livro "O Guia do Mochileiro das Galáxias" (The Hitchhiker's Guide to the Galaxy), de Douglas Adams, no qual o número 42 é revelado como "A Resposta para a Pergunta Fundamental sobre a Vida, o Universo e Tudo Mais".<br/><br/>
#         Nota: Tecnicamente, qualquer outro número inteiro (ex: random_state=0, random_state=1 ou random_state=123) funcionaria rigorosamente da mesma forma. O 42 tornou-se apenas o padrão não oficial mais popular na comunidade.</li>
#     </ul>
#     </li>
# </ul>

# 4. Modelo
model = Pipeline(
    steps=[
        ('preprocessor', preprocessor),
        ('classifier', LinearSVC(dual=False, random_state=42)),
    ]
)

# [markdown]
# <b>5 - Accurácia</b>

# [markdown]
# <b>Validação Cruzada (Cross-Validation)</b><br/><br/>
# É a melhor prática para datasets pequenos como o Titanic, pois avalia o modelo em múltiplos pedaços dos dados de treino sem perder dados.

# [markdown]
# <b>cv=5 -></b> O número de divisões (conhecido como folds ou "dobras"). <br/><br/>O número 5 significa que o algoritmo vai aplicar o método K-Fold com K=5. 
# <ul>
#     <li>Divide o X_train em 5 partes iguais.</li><br/>
#     <li>Em cada rodada, 4 partes são usadas para treinar o modelo e 1 parte é usada exclusivamente para testar. Isso se repete 5 vezes, de modo que cada uma das 5 partes seja usada exatamente uma vez como conjunto de teste/validação.</li><br/>
#     <li><b>scoring='accuracy':</b> A métrica de avaliação que você quer calcular em cada rodada. Nesse caso, a Acurácia (porcentagem de acertos = (previsões corretas / total de previsões).</li>
# </ul>

from sklearn.model_selection import cross_val_score

# Usando todo o df_train para validar em 5 subconjuntos (folds)
scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')

print(f'Acurácia Média (Cross-Validation): {scores.mean() * 100:.2f}%')

# [markdown]
# #### <b>MODELO RANDOM FOREST</b>

# [markdown]
# O modelo combina centenas de análises independentes, em vez de confiar em uma unica árvore de decisão.

# [markdown]
# <ul>
#     <li>Classificação: Votação Majoritária</li>
#     <li>Regressão: Média Matemática</li>
# </ul>

# [markdown]
# ![image.png](attachment:image.png)

# [markdown]
# <ul>
#     <li>Adequação do Modelo</li>
# </ul>

# [markdown]
# ![image.png](attachment:image.png)

# [markdown]
# <b>3 - Pipeline de Pré-processamento</b>

# [markdown]
# ![image.png](attachment:image.png)

# 3. Pipeline de Pré-processamento

preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(drop='first'), cat_cols)
    ]
)


# [markdown]
# <b>4 - Modelo</b>

# 4. Modelo
from sklearn.ensemble import RandomForestClassifier

model = Pipeline(
    steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(random_state=42))
    ]
)

# [markdown]
# <b>5 - Accurácia</b>



# [markdown]
# <b>6 - Treinamento</b>

# 5. Treinamento 
model.fit(X_train, y_train)

# [markdown]
# <b>7 - Predição</b>

# 6. Predição
predictions = model.predict(test)

df_predictions = test
df_predictions.insert(loc=1, column='survived', value=predictions)

df_predictions

# [markdown]
# <b>Preparando o Envio para o Kaggle

from pandas import DataFrame

df_envio = DataFrame(columns=['PassengerId', 'Survived'])  # Criar o DataFrame vazio
df_envio['PassengerId'] = df_predictions['passengerid']
df_envio['Survived'] = df_predictions['survived']
df_envio.to_csv('submission.csv', index=False)
df_envio

