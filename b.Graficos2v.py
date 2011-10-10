"""
Mestrado em Modelagem Matematica da Informacao
Disciplina de Modelagem e Mineracao de Dados
Professor: Renato Rocha Souza
Topic: Two Variables Graphs
"""

#Importing the packages that will be used
from numpy import loadtxt, arange, subtract, linspace
from matplotlib.pyplot import plot, scatter, boxplot, semilogx, semilogy, loglog, show, title, legend, figure
from scipy import linspace, polyval, polyfit, sqrt, stats, randn
from scipy.stats import linregress, describe
from pylab import hist, movavg

#Specifying the path to the files
datapath = "/home/rsouza/Dropbox/Renato/Python/DAWOST/datasets/datasets_dawost/"
dataset1 = "ch03_allometricscaling"
dataset2 = "ch03_DraftLottery"
dataset3 = "ch03_SunSpot_yearnum.dat"
dataset4 = "ch03_logscale"
dataset5 = "ch03_marathon.csv"

#loading the datasets
x = loadtxt(datapath+dataset1, usecols=(1,2), delimiter=',')
y = loadtxt(datapath+dataset2,usecols=(3,4), skiprows=39)
z = loadtxt(datapath+dataset3)
w = loadtxt(datapath+dataset4)
um = loadtxt(datapath+dataset5, usecols=(0,4), delimiter=';')
uf = loadtxt(datapath+dataset5, usecols=(0,8), delimiter=';', skiprows=69)

#http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.describe.html#scipy.stats.describe
describe(y)

#Scatter Plots
#http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.scatter

#plot(x[:,0], x[:,1], 'bo')
#plot(y[:,0], y[:,1], 'bo')
#plot(z[:,0], z[:,1], 'bo')
#scatter(x[:,0], x[:,1], c='b', marker = 'o')
#figure(2)
#scatter(z[:,0], z[:,1], c='r', marker = 'x')

#title('Tempos de corrida - Maratona de Boston')
#scatter(uf[:,0], uf[:,1], c='r', marker='+')
#scatter(um[:,0], um[:,1], c='b', marker='o')
#legend(['Mulheres','Homens'])
#show() 

#Smoothing

#plot(y[:,0], y[:,1], 'bo')
#figure(2)
#plot(movavg(y[:,1],3))
#figure(3)
#plot(movavg(y[:,1],9))
#figure(4)
#plot(movavg(y[:,1],365))
#show()

#Residuals

#res = subtract(y[1:-1,1],(movavg(y[:,1],3)))
#res = subtract(y[2:-2,1],(movavg(y[:,1],5)))
#plot(y[:,0], y[:,1], 'bo')
#plot(res)

#Logarithms
#http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.semilogx
#http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.semilogy
#http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.loglog

#plot(w[:,0], w[:,1], 'bo')
#scatter(x[:,0], x[:,1], c='b', marker = '+')
#semilogx(x[:,0], x[:,1], c='r', marker = 'x', ls = 'none')
#semilogy(x[:,0], x[:,1], c='r', marker = 'o', ls = 'none')
#loglog(x[:,0], x[:,1], 'go')

#Linear Regressions
#http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html#scipy.stats.linregress
#http://www.scipy.org/Cookbook/LinearRegression

t1 = linspace(1897,2011,len(um[:,0]))
t2 = linspace(1960,2011,len(uf[:,0]))

#regressao com polinomio de grau 1
#(am,bm)=polyfit(t1,um[:,1],1) 
#(af,bf)=polyfit(t2,uf[:,1],1)
#xm=polyval([am,bm],t1)
#xf=polyval([af,bf],t2)

#regressao com polinomio de grau 4
(am,bm,cm,dm,em)=polyfit(t1,um[:,1],4) 
(af,bf,cf,df,ef)=polyfit(t2,uf[:,1],4)
xm=polyval([am,bm,cm,dm,em],t1)
xf=polyval([af,bf,cf,df,ef],t2)

title('Boston Marathon - Exemplo de Regressao Linear')
scatter(t1, um[:,1], c='b', marker='o')
scatter(t2, uf[:,1], c='g', marker='+')
plot(t1, xm,'b.-')
plot(t2, xf,'r.-')
legend(['Regressao H','Regressao M','Mulheres','Homens'])
show()        