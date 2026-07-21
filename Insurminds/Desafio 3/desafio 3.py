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
                        str.strip()
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
# <b>Eliminando variáveis desnecessárias</b>

df_train.columns

df_train = df_train.drop(columns=['ticket','passengerid'],errors='ignore')
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
# <ul>
#     <li><b>Detectando valores faltantes, tipos de dados, quantidade de linhas e colunas</b></li>
#     <li><b>Normalizando os nomes das colunas</b></li>
#     <li><b>Porcentagem de valores nulos</b></li>
#     <li><b>Lidando com duplicatas, valores nulos e colunas bagunçadas (Padronizar colunas com valores categóricos)</b></li>
# </ul>

# [markdown]
# <ul>
#     <ul>
#         <li>Cheque a quantidade de duplicatas antes de remover. Para remover, use df.drop_duplicates()</li>
#         <li>Os valores nulos de colunas de valores numéricos, devem ser preenchidos com a média da coluna</li>
#         <li>Os valores nulos de colunas categóricas, devem ser preenchidas como "desconhecido"</li>
#         <li>'Capitalize' colunas com valores categóricos (Não é o caso deste dataframe)</li>
#         <li>Retirar símbolo de moedas de colunas com valores monetários, vírgulas ou pontos.</li>    
#         <li>Desconfie de colunas do tipo object</li>
#         <li>Utilize a lógica para outros tipos de colunas. Ex: coluna de quantidade com valores negativos</li>
#     </ul>
#     <li><b>Modificando nomes de colunas</b></li>
#     <li><b>Eliminando variáveis desnecessárias</b></li>
# </ul>

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
# <b>Eliminando variáveis desnecessárias</b>

df_test.columns

df_test = df_test.drop(columns=['ticket','passengerid'],errors='ignore')
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

df_total = df_train.groupby('sex')['name'].count().reset_index()
df_survived_sex = df_train.loc[df_train['survived'] == 1].groupby('sex')['name'].count().reset_index()

df_survived_sex['percentage'] = ((df_survived_sex['name'] / df_total['name']) * 100).round(2)
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

df_total = df_train.groupby('age')['name'].count().reset_index()

df_survived_ages = df_train.loc[df_train['survived'] == 1].groupby('age')['name'].count().reset_index()
df_survived_ages['percentage'] = ((df_survived_ages['name'] / df_total['name']) * 100).round(2)

df_survived_ages

import numpy as np
import matplotlib.pyplot as plt

plt.plot(df_survived_ages['age'], df_survived_ages['percentage'])

# 2. Calculando a linha de tendência (Regressão Linear)
# O número 1 indica que queremos uma linha reta (polinômio de grau 1)
# O que faz p np.polyfit e o polyid ?
coeficientes = np.polyfit(df_survived_ages['age'], df_survived_ages['percentage'],2) # Calcula a matemática por trás da curva, 
funcao_tendencia = np.poly1d(coeficientes) # e o np.poly1d transforma essa matemática em uma função prática que você pode usar para desenhar a linha ou prever valores.

# 3. Plotando a linha de tendência
plt.plot(df_survived_ages['age'], funcao_tendencia(df_survived_ages['age']), 
         color='red', linestyle='-', linewidth=2, label='Tendência')

plt.xlabel('idades')
plt.ylabel('Taxa de Sobrevivência (%)')
plt.title('Taxa de Sobrevivência x Idades')
plt.show()


# [markdown]
# Concluímos que taxa de sobrevivência veio diminuindo até os 30 anos para depois aumentar a partir dos 40. Ou seja, as menores idades e as maiores idades foram privilegiadas.

# [markdown]
# <b>Taxa de Sobrevivência x Classe do Passageiro</b>

df_total = df_train.groupby('passenger_class')['name'].count().reset_index()

df_survived_class = df_train.loc[df_train['survived'] == 1].groupby('passenger_class')['name'].count().reset_index()

df_survived_class['percentage'] = ((df_survived_class['name'] / df_total['name']) * 100).round(2)
df_survived_class


data = {'classes': df_survived_class['passenger_class'].to_list(), 'Taxa de sobrevivência': df_survived_class['percentage'].to_list()}

bars = plt.bar(data['classes'], data['Taxa de sobrevivência'], color='#1f77b4')


# Adicionando os rótulos no topo das barras
# O parâmetro fmt='%.1f%%' formata o número com uma casa decimal e o símbolo de %
plt.bar_label(bars, fmt='%.1f%%', padding=1) 

plt.xlabel('Classe do Passageiro')
plt.ylabel('Taxa de Sobrevivência(%)')
plt.title('Taxa de Sobrevivência x Classe do Passageiro')
 
plt.show()


# [markdown]
# Concluímos que a taxa de sobrevivencia diminui nas classes 2 e 3 e aumenta na classe 1

# [markdown]
# <b>Taxa de Sobrevivencia x Tamanho da Família (Pais, filhos e parentes)</b>

# [markdown]
# Foi necessária a criação de uma nova variável chamada tamanho de família

df_total = df_train[['name','parents_children', 'siblings']]
df_total = df_total.groupby(['parents_children','siblings'])['name'].count().reset_index()
df_total['size'] = df_total['parents_children'] + df_total['siblings']
df_total = df_total.groupby('size')['name'].sum().reset_index()
df_total

df_survived_familysize = df_train.loc[df_train['survived'] == 1][['name','parents_children', 'siblings']]
df_survived_familysize = df_survived_familysize.groupby(['parents_children','siblings'])['name'].count().reset_index()
df_survived_familysize['size'] = df_survived_familysize['parents_children'] + df_survived_familysize['siblings']
df_survived_familysize = df_survived_familysize.groupby('size')['name'].sum().reset_index()
df_survived_familysize['percentage'] = ((df_survived_familysize['name'] / df_total['name']) * 100).round(2)
df_survived_familysize

data = {'tamanho': df_survived_familysize['size'].to_list(), 'Taxa de sobrevivência': df_survived_familysize['percentage'].to_list()}

bars = plt.bar(data['tamanho'], data['Taxa de sobrevivência'])

plt.bar_label(bars, fmt='%.1f%%', padding=1) 

# 2. Calculando a linha de tendência (Regressão Linear)
# O número 1 indica que queremos uma linha reta (polinômio de grau 1)
coeficientes = np.polyfit(df_survived_familysize['size'], df_survived_familysize['percentage'], 2) 
funcao_tendencia = np.poly1d(coeficientes)

# 3. Plotando a linha de tendência
plt.plot(df_survived_familysize['size'], funcao_tendencia(df_survived_familysize['size']), 
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
df_correlacao = df_train.corr(numeric_only=True).round(2)

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
#     <li><b>Relação entre Classe e Tarifa (passenger_class vs fare = -0.55):</b> Esta é a correlação negativa mais forte do conjunto. Faz total sentido prático: quanto menor o número da classe (1ª classe), significativamente maior o preço cobrado pela passagem.</li><br/>
#     <li><b>Estrutura Familiar Integrada (siblings vs parents_children = +0.41):</b>Correlação positiva moderada. Passageiros que viajavam com irmãos/cônjuges (siblings) frequentemente também estavam acompanhados de pais/filhos (parents_children), indicando grupos familiares maiores a bordo.</li><br/>
#     <li><b>Idade e Classe (age vs passenger_class = -0.34):</b>Correlação negativa moderada. Passageiros mais velhos tendiam a ocupar classes superiores (1ª classe), enquanto os passageiros mais jovens estavam predominantemente na 3ª classe.</li><br/>
#     <li><b>Idade e Acompanhantes (age vs siblings = -0.23 / parents_children = -0.18):</b>Relação negativa leve: passageiros mais jovens tendiam a viajar com mais familiares/irmãos do que pessoas mais velhas.</li>
# <ul>

