#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Mestrado em Modelagem Matematica da Informacao
Master Program - Mathematical Modeling of Information

Disciplina: Modelagem e Mineracao de Dados
Course: Data Mining and Modeling

Professor: Renato Rocha Souza
Topic: Two Variables Graphs (class #3)

Information on the Python Packages used:
http://docs.scipy.org/doc/
http://numpy.scipy.org/
http://scipy.org/
http://matplotlib.sourceforge.net/
'''

from numpy import loadtxt, genfromtxt, arange, subtract, linspace
from matplotlib.pyplot import plot, scatter, boxplot, semilogx, semilogy, loglog, show, title, legend, figure
from scipy import linspace, polyval, polyfit, sqrt, stats, randn
from scipy.stats import linregress, describe
from pylab import hist, movavg

'''Specifying the path to the files'''
datapath = "/home/rsouza/Documentos/Git/MMD/datasets/"
dataset1 = "ch03_allometricscaling"
dataset2 = "ch03_DraftLottery"
dataset3 = "ch03_SunSpot_yearnum.dat"
dataset4 = "ch03_logscale"
dataset5 = "ch03_marathon"

'''loading the datasets
http://docs.scipy.org/doc/numpy/reference/generated/numpy.loadtxt.html'''
allo = loadtxt(datapath+dataset1, usecols=(1,2), delimiter=',')
lottery = loadtxt(datapath+dataset2,usecols=(3,4), skiprows=39)
sunspot = loadtxt(datapath+dataset3)
logexample = loadtxt(datapath+dataset4)
marathon_m = loadtxt(datapath+dataset5, usecols=(0,4), delimiter=';')
marathon_w = loadtxt(datapath+dataset5, usecols=(0,8), delimiter=';', skiprows=69)

'''http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.describe.html#scipy.stats.describe'''
print(describe(allo))

'''Scatter Plots
http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.scatter'''
#plot(allo[:,0], allo[:,1])
#figure(2)
#scatter(allo[:,0], allo[:,1])
#figure(3)
#plot(sunspot[:,0], sunspot[:,1])
#figure(4)
#scatter(sunspot[:,0], sunspot[:,1], c='r', marker='x')
#figure(5)
#scatter(lottery[:,0], lottery[:,1], c='b', marker='o')
#figure(6)
#scatter(marathon_m[:,0], marathon_m[:,1], c='b', marker='+')
#scatter(marathon_w[:,0], marathon_w[:,1], c='r', marker='.')
#title('Final times - Boston Marathon')
#legend(['Men','Women'])
#show()

'''Treating Logarithmic Data
http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.semilogx
http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.semilogy
http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.loglog'''
#scatter(logexample[:,0], logexample[:,1], c='r', marker = 'o')
#figure(2)
#scatter(allo[:,0], allo[:,1], c='b', marker='+')
#figure(3)
#semilogx(allo[:,0], allo[:,1], c='r', marker='x', ls='none')
#figure(4)
#semilogy(allo[:,0], allo[:,1], c='r', marker='o', ls='none')
#figure(5)
#loglog(allo[:,0], allo[:,1], c='g', marker='o', ls='none')


'''Smoothing with moving averages
http://matplotlib.sourceforge.net/api/mlab_marathon_mapi.html'''
#scatter(lottery[:,0], lottery[:,1], c='b', marker='+')
#figure(2)
#scatter(lottery[1:-1,0], movavg(lottery[:,1],3), c='r', marker='+')
#figure(3)
#plot(movavg(lottery[:,1],15), c='g', marker='.')
#figure(4)
#plot(movavg(lottery[:,1],33))
#figure(5)
#plot(movavg(lottery[:,1],365))
#show()

'''Residuals
http://docs.scipy.org/doc/numpy/reference/generated/numpy.subtract.html
'''
#plot(movavg(sunspot[:,1],15))
#res = subtract(sunspot[3:-3,1],(movavg(sunspot[:,1],9)))
#res = subtract(sunspot[15:-15,1],(movavg(sunspot[:,1],31)))
#res = subtract(sunspot[45:-45,1],(movavg(sunspot[:,1],91)))
#figure(2)
#plot(sunspot[45:-45,1], c='g', marker='.')
#plot(res, c='r', marker='.')
#figure(3)
#plot(movavg(res,21))

'''Linear and Polynomial Regressions
http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html#scipy.stats.linregress
http://www.scipy.org/Cookbook/LinearRegression
http://en.wikipedia.org/wiki/Linear_regression
http://en.wikipedia.org/wiki/Polynomial_regression
'''
t1 = linspace(1897,2011,len(marathon_m[:,0]))
t2 = linspace(1960,2011,len(marathon_w[:,0]))

#linear regression 
(a,b) = polyfit(t1,marathon_m[:,1],1) 
xm_linear = polyval([a,b],t1)
(a,b) = polyfit(t2,marathon_w[:,1],1)
xf_linear = polyval([a,b],t2)

#regressao with 4th order polynomial
(a,b,c,d,e) = polyfit(t1,marathon_m[:,1],4) 
xm_4th = polyval([a,b,c,d,e],t1)
(a,b,c,d,e) = polyfit(t2,marathon_w[:,1],4)
xw_4th = polyval([a,b,c,d,e],t2)

#plotting the graph(1)
title('Boston Marathon - yearly best times')
scatter(t1, marathon_m[:,1], c='b', marker='o')
scatter(t2, marathon_w[:,1], c='g', marker='+')
plot(t1, xm_linear,'b.-')
plot(t2, xf_linear,'r.-')
legend(['Linear Reg M','Linear Reg W','Men','Women'])

#plotting the graph(2)
figure(2)
title('Boston Marathon - yearly best times')
scatter(t1, marathon_m[:,1], c='b', marker='o')
scatter(t2, marathon_w[:,1], c='g', marker='+')
plot(t1, xm_4th,'b.-')
plot(t2, xw_4th,'r.-')
legend(['4th Pol Reg M','4th Pol Reg W','Men','Women'])

show()        