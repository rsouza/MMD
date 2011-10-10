""" 
Mestrado em Modelagem Matematica da Informacao
Disciplina de Modelagem e Mineracao de Dados
Professor: Renato Rocha Souza
Topico: Analise de series temporais
"""

#Importing the packages that will be used
# Pylab = NumPy, SciPy, Matplotlib, and IPython

from numpy import loadtxt, arange, subtract, linspace, concatenate, zeros_like
from matplotlib.pyplot import plot, scatter, boxplot, semilogx, semilogy, loglog, show, title, legend, figure
from scipy import linspace, polyval, polyfit, sqrt, stats, randn
from scipy.stats import linregress, describe
from scipy.signal import gaussian, convolve, mean, correlate
from pylab import hist, movavg

#Specifying the path to the files
datapath = "/home/rsouza/Dropbox/Renato/Python/DAWOST/datasets/"
dataset = "cotacoesbovespa.csv"

cotacoes = loadtxt(datapath+dataset, delimiter=",", skiprows = 1, converters = {0: datestr2num})

#Extraindo as dimensoes do array - numero de pontos e de variaveis da serie
dimlinhas = cotacoes.shape[0] #Igual ao comando: len(cotacoes[:,0])
dimcolunas = cotacoes.shape[1] #Igual ao comando: len(cotacoes[0,:]) 

#Verificando o "jeitao" da serie pela primeira vez
#plot (cotacoes[:,0], cotacoes[:,1])

#Ordenando os pontos de data na coluna zero com argsort()
#cotord = cotacoes[cotacoes[:,0].argsort(),:]

#Pode-se ver que o grafico eh o mesmo apos a reordenacao
#title('Serie Original')
#plot (cotord[:,0], cotord[:,1])

#Excluindo os dados anteriores a mudanca de escala
cotacoes2 = cotacoes[0:3555,:]
cotord2 = cotacoes2[cotacoes2[:,0].argsort(),:]
#title('Serie Original truncada')
#plot (cotord2[:,0], cotord2[:,1])

# Buscando por versoes suavizadas da serie temporal:
# (deslocando os dados somando uma constante)
#figure(2)
#title('Suavizacao - janela de uma semana')
#plot (cotord2[5:-5,0], movavg(cotord2[:,1]+10000,11)) 
#figure(3)
#title('Suavizacao - janela de um mes')
#plot (cotord2[10:-10,0], movavg(cotord2[:,1]+20000,21))
#figure(4)
#title('Suavizacao - janela de seis meses')
#plot (cotord2[60:-60,0], movavg(cotord2[:,1]+30000,121))


# Buscando por uma versao suavizada da serie temporal:

# 1) Construir um filtro gaussiano de 31 pontos com desvio padrao = 4
filt = gaussian(31, 4)
#plot (filt)

# 2) Normalizando o filtro dividindo pela soma dos elementos
filt /= sum(filt)

# 3) Convoluindo a serie com o filtro
cotord2suave = convolve(cotord2[:,1], filt, mode='valid')

# Mostrando as series original e suavizada conjuntamente:
#figure(5, figsize=(14,10))
#plot(cotord2[:,0], cotord2[:,1], 'r' )
#plot (cotord2[10:-10,0], movavg(cotord2[:,1]-9000,21), 'g')
#plot (cotord2[15:-15,0], cotord2suave+9000, 'b')

#Calculando a funcao de autocorrelacao:
# 1) Subtraindo a media 
cotsubmedia = cotord2suave - mean(cotord2suave)
# 2) Acrescentando aa serie um vetor de zeros de mesmo tamanhos, aplicando a funcao correlacao
corr = correlate(cotsubmedia, concatenate((cotsubmedia,zeros_like(cotsubmedia))), mode='valid')
# 3) opcional: analise apenas um grupo de elementos
corr = corr[:1000]
# 4) Normalize dividindo pelo valor do primeiro elemento
corr /= corr[0]

figure(6, figsize=(14,10))
title('Funcao de Autocorrelacao')
plot(corr)
