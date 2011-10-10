""" 
Mestrado em Modelagem Matematica da Informacao
Disciplina de Modelagem e Mineracao de Dados
Professor: Renato Rocha Souza
Primeiro exercicio em sala
"""

#Importing the packages that will be used
from numpy import loadtxt, unique, cov, corrcoef, empty
from matplotlib.pyplot import plot, scatter, show, title, legend, figure
from scipy.stats import describe, rv_discrete
from pylab import hist, movavg

#Specifying the path to the files
datapath = "/home/rsouza/Dropbox/Renato/Python/DAWOST/datasets/GenderTrainingSet/"
dataset1 = "GenderTrainingSet.csv"


#loading the dataset
v = loadtxt(datapath+dataset1, delimiter=',',skiprows=2)


def bstats(vec):
    s = {'num_element':len(vec), 'minimo':vec.min(),
         'maximo':vec.max(), 'media':vec.mean(),
         'desvio_padrao':vec.std()}
    return s

#bstats(v[:,0])
#plot(v[:,0])
#plot(sort(v[:,0]))
#hist(v[:,0], bins=40)
#len(unique(v[:,12]))
#len(unique(v[:,13]))

idades = unique(v[:,0])
sujeitos = unique(v[:,12])

def secoessujeito(vec,nsujeito):
    sujeitos = unique(vec[:,12])
    s = unique(vec[:,13][vec[:,12] == sujeitos[nsujeito]])
    return s

sessoes_sujeito = secoessujeito(v,1)

def plotatemp(vec, sessoes_sujeito):
    for i in range(len(sessoes_sujeito)):
        #intervalos de tempo da sessao
        x = vec[vec[:,13] == sessoes_sujeito[i],14]
        #fluxo de temperatura
        y1 = vec[vec[:,13] == sessoes_sujeito[i],3]
        y1norm = y1/max(y1)
        y1norm_mavg = movavg(y1norm,11)        
        #temperatura proxima ao corpo
        y2 = vec[vec[:,13] == sessoes_sujeito[i],5]
        y2norm = y2/max(y2)        
        y2norm_mavg = movavg(y2norm,3)
        #temperatura da pele
        y3 = vec[vec[:,13] == sessoes_sujeito[i],7]
        y3norm = y3/max(y3)        
        y3norm_mavg = movavg(y3norm,3)

        figure(i+1)        
        #scatter(x,y1, c='r', marker = 'o')
        #scatter(x,y2, c='b', marker = 'o')
        #scatter(x,y3, c='g', marker = 'o')
        #scatter(x,y1norm, c='r', marker = 'o')
        #scatter(x,y2norm, c='b', marker = 'o')
        #scatter(x,y3norm, c='g', marker = 'o')
        #scatter(x,y2-y3, c='g', marker = 'o')
        scatter(x[5:-5],y1norm_mavg, c='r', marker = '+')
        scatter(x[1:-1],y2norm_mavg-0.2, c='b', marker = 'o')
        scatter(x[1:-1],y3norm_mavg, c='g', marker = 'o')
    show()

def plotaacelerom(vec, sessoes_sujeito):
    for i in range(len(sessoes_sujeito)):
        #intervalos de tempo da sessao
        x = vec[vec[:,13] == sessoes_sujeito[i],14]
        xtrim = x[5:-5]
        #pedometro
        y1 = vec[vec[:,13] == sessoes_sujeito[i],6]
        y1norm = y1/max(y1)
        y1norm_mavg = movavg(y1norm,11)        
        # acelerometro 1        
        y2 = vec[vec[:,13] == sessoes_sujeito[i],8]
        y2norm = y2/max(y2)        
        y2norm_mavg = movavg(y2norm,11)
        # acelerometro 2        
        y3 = vec[vec[:,13] == sessoes_sujeito[i],9]
        y3norm = y3/max(y3)        
        y3norm_mavg = movavg(y3norm,11)
        # acelerometro 3        
        y4 = vec[vec[:,13] == sessoes_sujeito[i],10]
        y4norm = y4/max(y4)        
        y4norm_mavg = movavg(y4norm,11)
        # acelerometro 4        
        y5 = vec[vec[:,13] == sessoes_sujeito[i],11]
        y5norm = y5/max(y5)        
        y5norm_mavg = movavg(y5norm,11)
        
        figure(i+1)
        #scatter(xtrim,y1norm_mavg, c='g', marker = 'o')
        scatter(xtrim,y2norm_mavg, c='r', marker = '>')
        #scatter(xtrim,y3norm_mavg, c='r', marker = '<')
        scatter(xtrim,y4norm_mavg, c='b', marker = '>')
        #scatter(xtrim,y5norm_mavg, c='b', marker = '<')
    show()

#plotatemp(v,sessoes_sujeito)
#plotaacelerom(v,sessoes_sujeito)

def depend(vec,sessao_sujeito,var1,var2):
    x = vec[vec[:,13] == sessao_sujeito,var1]
    y = vec[vec[:,13] == sessao_sujeito,var2]
    #http://docs.scipy.org/doc/numpy/reference/generated/numpy.cov.html    
    #http://en.wikipedia.org/wiki/Covariance 
    vcov = cov(x,y,rowvar=0)
    #http://docs.scipy.org/doc/numpy/reference/generated/numpy.corrcoef.html
    #http://en.wikipedia.org/wiki/Correlation_and_dependence
    vcorrc = corrcoef(x,y,rowvar=0)
    return x,y,vcov,vcorrc

#(a,b,cov_ab,corrc_ab) = depend(v,sessoes_sujeito[1],9,10)
#print "Variancia de var1:", cov_ab[0,0]
#print "Variancia de var1:", cov_ab[1,1]
#print "Covariancia var1 x var2:", cov_ab[1,0]
#print "Covariancia var2 x var1:", cov_ab[0,1]
#print "Coeficiente de correlacao var1 x var2:", corrc_ab[0,1]
#print "Coeficiente de correlacao var2 x var1:", corrc_ab[1,0]

def matrizcov(vec,sessao_sujeito):
    mcov = empty([14,14])
    mcorr = empty([14,14])
    for i in range(0,14):
        for j in range(0,14):
            #x = vec[vec[:,13] == sessao_sujeito,i]
            #y = vec[vec[:,13] == sessao_sujeito,j]
            x = vec[:,i]
            y = vec[:,j]
            mcov[i,j] = cov(x,y,rowvar=0)[0,1]
            mcorr[i,j] = corrcoef(x,y,rowvar=0)[0,1]
    return mcov, mcorr

matcov = matrizcov(v,sessoes_sujeito[1])[0]
#for i in range(0,13):
#    figure(i+1)
#    plot(matcov[i])
#show()

matcorr = matrizcov(v,sessoes_sujeito[1])[1]
for i in range(0,13):
    #figure(i+1)
    #plot(matcorr[i])
    plot(matcorr[i],'o')
show()