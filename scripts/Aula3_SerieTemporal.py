#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Mestrado em Modelagem Matematica da Informacao
Master Program - Mathematical Modeling of Information

Disciplina: Modelagem e Mineracao de Dados
Course: Data Mining and Modeling

Professor: Renato Rocha Souza
Topic: Two Variables Graphs - Temporal Series (class #3)

Information on the Python Packages used:
http://docs.scipy.org/doc/
http://numpy.scipy.org/
http://scipy.org/
http://matplotlib.sourceforge.net/
'''

from numpy import loadtxt, arange, subtract, linspace, concatenate, zeros_like
from matplotlib.pyplot import plot, scatter, boxplot, semilogx, semilogy, loglog, show, title, legend, figure
from scipy import linspace, polyval, polyfit, sqrt, stats, randn
from scipy.stats import linregress, describe
from scipy.signal import gaussian, convolve, mean, correlate
from pylab import hist, movavg

'''Specifying the path to the files'''
datapath = "/home/rsouza/Documentos/Git/MMD/datasets/"
dataset = "cotacoesbovespa.txt"

'''loading the dataset
http://docs.scipy.org/doc/numpy/reference/generated/numpy.loadtxt.html'''
cotacoes = loadtxt(datapath+dataset, delimiter=",", skiprows = 1, converters = {0: datestr2num})

'''Examining the dimensions of the dataset'''
print(cotacoes.shape)
lines = cotacoes.shape[0] #same as: len(cotacoes[:,0])
columns = cotacoes.shape[1] #same as: len(cotacoes[0,:]) 

'''plotting for the first time - exploring'''
plot(cotacoes[:,0], cotacoes[:,1])
title('Bovespa Historical Series')

'''And what if the dates were not ordered?
We can use argsort to order an array by one of its columns (or rows)
http://docs.scipy.org/doc/numpy-1.5.x/reference/generated/numpy.argsort.html'''
ord_cot = cotacoes[cotacoes[:,0].argsort(),:]

'''We can see there is a great scale change... 
maybe it's a good idea to treat as two separate series'''
cot_after = cotacoes[0:3555,:]
figure(2)
title('Bovespa Trunked Series')
plot(cot_after[:,0], cot_after[:,1])

'''Applying smoothing, as before,
with windows varying its size:'''
figure(3)
title('Bovespa - one week smoothing')
plot (cot_after[5:-5,0], movavg(cot_after[:,1],11)) 
figure(4)
title('Bovespa - one month smoothing')
plot (cot_after[10:-10,0], movavg(cot_after[:,1],21)) 
figure(5)
title('Bovespa - six months smoothing')
plot (cot_after[60:-60,0], movavg(cot_after[:,1],121)) 

'''Smoothing with a gaussian filter
1) Building a gaussian filter with 31 points and standard deviation of 4
2) Normalizing the filter dividing by the sum of the elements'''

filt = gaussian(31, 4)
filt /= sum(filt)

figure(6)
plot (filt)

# 3) Convoluindo a serie com o filtro
#cotord2suave = convolve(cotord2[:,1], filt, mode='valid')

# Mostrando as series original e suavizada conjuntamente:
#figure(5, figsize=(14,10))
#plot(cotord2[:,0], cotord2[:,1], 'r' )
#plot (cotord2[10:-10,0], movavg(cotord2[:,1]-9000,21), 'g')
#plot (cotord2[15:-15,0], cotord2suave+9000, 'b')

#Calculando a funcao de autocorrelacao:
# 1) Subtraindo a media 
#cotsubmedia = cotord2suave - mean(cotord2suave)
# 2) Acrescentando aa serie um vetor de zeros de mesmo tamanhos, aplicando a funcao correlacao
#corr = correlate(cotsubmedia, concatenate((cotsubmedia,zeros_like(cotsubmedia))), mode='valid')
# 3) opcional: analise apenas um grupo de elementos
#corr = corr[:1000]
# 4) Normalize dividindo pelo valor do primeiro elemento
#corr /= corr[0]

#figure(6, figsize=(14,10))
#title('Funcao de Autocorrelacao')
#plot(corr)
