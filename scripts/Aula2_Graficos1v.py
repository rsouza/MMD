#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Mestrado em Modelagem Matematica da Informacao
Master Program - Mathematical Modeling of Information

Disciplina: Modelagem e Mineracao de Dados
Course: Data Mining and Modeling

Professor: Renato Rocha Souza
Topic: Simple Univariate Graphs (class #2)

Information on the Python Packages used:
http://docs.scipy.org/doc/
http://numpy.scipy.org/
http://scipy.org/
http://matplotlib.sourceforge.net/
'''

import numpy as np
from numpy import loadtxt, genfromtxt, array, arange
from matplotlib.pyplot import plot, boxplot, show, title, legend, figure
from scipy.stats import describe, cumfreq
from scipy.stats.kde import gaussian_kde
from pylab import hist

'''Specifying the path to the files'''
datapath = "/home/rsouza/Documentos/Git/MMD/datasets/"
dataset1 = "ch02_presidents"
dataset2 = "ch02_serverdata"
dataset3 = "ch02_glass.data"

'''Gathering some information on the datasets'''
def bstats(vec):
    s = {'num_element':len(vec), 'minimo':vec.min(),
         'maximo':vec.max(), 'media':vec.mean(),
         'desvio_padrao':vec.std()}
    return s

'''Jitter Plots
http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.plot'''
def jitterplots(vec):
    plot(vec)
    title('default settings')
    legend('data')
    figure(2)
    plot(vec,'r')
    title('default + red')    
    figure(3)
    plot(vec,'bo')
    title('blue and circles')
    figure(4)
    plot(vec,'g.')
    title('green and dots')
    show()
    
'''Histograms
http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.hist'''
def histo(vec, nbins=100):
    hist(vec, bins=nbins)
    figure(2)
    hist(vec, bins=10*nbins)
    figure(3)
    hist(vec, bins=100*nbins)
    show()

'''Kernel Density Estimates
http://www.scipy.org/doc/api_docs/SciPy.stats.kde.gaussian_kde.html'''
def kerndens(vec,nbins=100):
    hist(vec, bins=nbins, normed=True, align='mid')
    figure(2)    
    gkde = gaussian_kde(vec)
    plot(arange(0,(1.01*(max(vec)-min(vec))),.1),
         gkde.evaluate(arange(0,(1.01*(max(vec)-min(vec))),.1)))   
    show()

'''Cumulative Frequency
http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.cumfreq.html#scipy.stats.cumfreq'''
def cumdist(vec, nbins=100):
    hist(vec, bins=nbins, normed=False, align='mid')
    figure(2)    
    disc = cumfreq(vec, numbins=nbins)
    plot(disc[0]/len(vec)) 
    show()

'''Box and Whisker Plots
http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.boxplot'''
def bp(vec):
    boxplot(vec, notch=0, sym='+', vert=0, whis=1.5,
            positions=None, widths=None)
    show()


if __name__ == '__main__':
    '''loading the datasets
    http://docs.scipy.org/doc/numpy/reference/generated/numpy.genfromtxt.html'''
    #x = genfromtxt(datapath+dataset1, usecols=(1,2), dtype=(str,int))
    x = genfromtxt(datapath+dataset1, usecols=(2))
    x_names = genfromtxt(datapath+dataset1, usecols=(1), dtype=(str))
    #x = genfromtxt(datapath+dataset1, usecols=(1,2), names = ['presidents','months'],dtype=[('names','|S12'),('months','i8')])
    #x = np.array([[t[0] for t in x],[t[1] for t in x]]).T
    
    '''http://docs.scipy.org/doc/numpy/reference/generated/numpy.loadtxt.html'''
    y = loadtxt(datapath+dataset2)
    z = loadtxt(datapath+dataset3, usecols=(1,2,10), delimiter=',')
    
    '''http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.describe.html'''
    #print(describe(x[:,1]))
    print(describe(y))
    print(describe(z))
    print
    
    '''Customized version: bstats'''
    print(bstats(x))
    print(bstats(y))
    print(bstats(z[:,1]))

    '''Examining with Jitter Plots'''
    #jitterplots(x)

    '''Examining with Histograms
    Try to change the default bins value'''
    #histo(x, 10)
    #histo(y, 10)

    '''Kernel Density Estimates
    http://www.scipy.org/doc/api_docs/SciPy.stats.kde.gaussian_kde.html'''
    #kerndens(y)

    '''Cumulative Frequency
    http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.cumfreq.html#scipy.stats.cumfreq'''
    #cumdist(x)
    
    '''Box and Whisker Plots
    http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.boxplot'''
    #bp(x)
    #bp(z[:,0])