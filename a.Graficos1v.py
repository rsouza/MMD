"""
Mestrado em Modelagem Matematica da Informacao
Disciplina de Modelagem e Mineracao de Dados
Professor: Renato Rocha Souza
Topic: Simple Univariate Graphs
"""

#Importing the packages that will be used
# Pylab = NumPy, SciPy, Matplotlib, and IPython
from numpy import loadtxt, arange
from matplotlib.pyplot import plot, scatter, boxplot, show, title, legend, figure
from scipy import linspace, polyval, polyfit, sqrt, stats, randn
from scipy.stats import describe, cumfreq
from scipy.stats.kde import gaussian_kde
from pylab import hist

#Specifying the path to the files
datapath = "/home/rsouza/Dropbox/Renato/Python/DAWOST/datasets/"
dataset1 = "ch02_presidents"
dataset2 = "ch02_serverdata"
dataset3 = "ch02_glass.data"

#loading the datasets
x = loadtxt(datapath+dataset1, usecols=(2,))
y = loadtxt(datapath+dataset2)
z = loadtxt(datapath+dataset3, usecols=(1,10), delimiter=',')

#http://scipy.org/
def bstats(vec):
    s = {'num_element':len(vec), 'minimo':vec.min(),
         'maximo':vec.max(), 'media':vec.mean(),
         'desvio_padrao':vec.std()}
    return s

#http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.describe.html#scipy.stats.describe
describe(y)

#Jitter Plots
#http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.plot
def jitterplots(vec):
    plot(vec)
    figure(2)
    plot(vec,'r')
    figure(3)
    plot(vec,'bo')
    figure(4)
    plot(vec,'g.')
    show()
    
#Histograms
#http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.hist
def histo(vec, nbins=100):
    hist(vec, bins=nbins)
    figure(2)
    hist(vec, bins=10*nbins)
    figure(3)
    hist(vec, bins=100*nbins)
    show()

#Kernel Density Estimates
#http://www.scipy.org/doc/api_docs/SciPy.stats.kde.gaussian_kde.html
def kerndens(vec,nbins=100):
    hist(vec, bins=nbins, normed=True, align='mid')
    figure(2)    
    gkde = gaussian_kde(vec)
    plot(arange(0,(1.01*(max(vec)-min(vec))),.1),
         gkde.evaluate(arange(0,(1.01*(max(vec)-min(vec))),.1)))   
    show()

#Cumulative Frequency
#http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.cumfreq.html#scipy.stats.cumfreq
def cumdist(vec, nbins=100):
    hist(vec, bins=nbins, normed=False, align='mid')
    figure(2)    
    disc = cumfreq(vec, numbins=nbins)
    plot(disc[0]/len(vec)) 
    show()

#Box and Whisker Plots
def bp(vec):
    boxplot(vec, notch=0, sym='+', vert=0, whis=1.5,
            positions=None, widths=None)
    show()
#bp(z[:,0])