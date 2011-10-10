""" 
Mestrado em Modelagem Matematica da Informacao
Disciplina de Modelagem e Mineracao de Dados
Professor: Renato Rocha Souza
Topico: Clustering de feeds rss
"""

import feedparser #http://www.feedparser.org/
import re #http://docs.python.org/library/re.html
from PIL import Image,ImageDraw #http://www.pythonware.com/library/pil/handbook/index.htm
from math import sqrt
import random

#Especificando o caminho para o arquivo
datapath = "/home/rsouza/Dropbox/Renato/Python/MMD/"
listafeeds = "feedlist.txt"
stopwords = "stopwords.txt"
saida = "output.txt"
dendrog1 = "feedclusters.jpg"
dendrog2 = "wordclusters.jpg"
g2d1 = "g2dfeeds.jpg"
g2d2 = "g2dwords.jpg"
lfeeds = (datapath+listafeeds)
lstopwords = (datapath+stopwords)
fsaida = (datapath+saida)
dendsaida = (datapath+dendrog1)
dendsaida2 = (datapath+dendrog2)
g2dsaida = (datapath+g2d1)
g2dsaida2 = (datapath+g2d2)
feedlist=[line for line in file(lfeeds)] #Le a lista de blogs no arquivo especificado

""" Bloco de funcoes de leitura dos feeds e contagem das palavras """

def getwords(html): # "Limpa" o conteudo de um arquivo html
    # Remove as tags HTML
    txt = re.compile(r'<[^>]+>').sub('',html)
    # Separa as palavras pelos caracteres nao alfabeticos
    words = re.compile(r'[^A-Z^a-z]+').split(txt)
    # Converte para minuscula
    return [word.lower() for word in words if word!='']

def getwordcounts(url): # Devolve titulo e dicionario com contagem de palavras de um feed RSS
    # Parse the feed
    d = feedparser.parse(url)
    wc = {}
    # Para cada uma das entradas do feed, procura-se pelo resumo ('summary' ou 'description')
    for entry in d.entries:
        if 'summary' in entry:
            summary = entry.summary
        else:
            summary = entry.description
            # Para cada uma das entradas do feed, contam-se as palavras
        words = getwords(entry.title+' '+summary)
        """ (opcional) Retira as stopwords """
        stoplist = file(lstopwords).readlines()
        stoplist = [word.strip() for word in stoplist]
        words = [word for word in words if word not in stoplist]
        # Preenche o dicionario no formato {palavra: num aparicoes}        
        for word in words:
            wc.setdefault(word,0) # O valor padrao de aparicoes e zero
            wc[word] += 1 # Se ela ocorre, incrementa-se o valor
    return d.feed.title,wc

def getwordcountfeeds(lfeeds, feedlist):
    apcount = {} #Dicionario que guardara os blogs em que uma palavra aparece
    wordcounts = {} #Dicionario que guardara a quantidade de vezes que uma palavra aparece em um blog
    #Tenta acessar o feed atraves da funcao getwordcount
    for feedurl in feedlist:
        try:
            title,wc = getwordcounts(feedurl)
            wordcounts[title] = wc
            for word,count in wc.items():
                apcount.setdefault(word,0)
                if count > 1:
                    apcount[word] += 1
        except:
            print 'Falha ao acessar o feed %s' % feedurl
    return apcount, wordcounts

def neither_common_nor_rare(apcount, feedlist):
    """ (opcional) Seleciona apenas as palavras que aparecem em certo numero mas nao em todos os blogs"""
    wordlist = []
    for w,bc in apcount.items():
        frac = float(bc)/len(feedlist)
        if frac > 0.1 and frac < 0.9: #ajustar estes parametros
            wordlist.append(w)
    return wordlist
    
""" Bloco de funcoes para salvamento e leitura de arquivos para persistencia de dados """

def createoutputfile(wordlist, wordcounts, filename):
    """ Salva o arquivo com o nome dos feeds, as palavras e a frequencia desta nos feeds"""
    out = file(filename,'w')
    out.write('Feed') #escreve 'Feed' acima do que sera a coluna de nomes de feeds
    for word in wordlist: out.write('\t%s' % word) #na mesma linha, escreve uma lista de palavras separadas por <tab>
    out.write('\n') #pula uma linha
    # a partir de entao, gera uma linha para cada feed, com as frequencias das palavras
    for feed,wc in wordcounts.items():
        print 'Processado o feed: ', feed 
        out.write(feed)
        for word in wordlist:
            if word in wc: out.write('\t%d' % wc[word])
            else: out.write('\t0')
        out.write('\n')

def readfile(filename):
    """ Le o arquivo salvo, reformatando os dados"""
    lines = [line for line in file(filename)]
    # Primeira linha do arquivo sao 
    colnames = lines[0].strip().split('\t')[1:] #separa a primeira linha pelos <tabs>; ignora "Blog"
    rownames = []
    data = []
    for line in lines[1:]: #itera sobre a linha 2(1) em diante...
        p = line.strip().split('\t') #separa por <tabs>
        # Primeira coluna da linha e o nome do feed/site
        rownames.append(p[0])
        # Os dados (frequencia de palavras) estao no resto da linha
        data.append([float(x) for x in p[1:]])
    return rownames,colnames,data

def rotatematrix(data):
    newdata = []
    for i in range(len(data[0])):
        newrow = [data[j][i] for j in range(len(data))]
        newdata.append(newrow)#separa a primeira linha pelas virgulas
    return newdata

""" Bloco de calculo de clusters """

class bicluster:
    """Classe para representar o objeto cluster"""
    def __init__(self,vec,left = None, right = None,distance = 0.0,id = None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance

def pearson(v1,v2):
    """Um dos muitos algoritmos para calcular correlacao,
    alternativa ao calculo pela distancia euclideana"""
    # Simple sums
    sum1 = sum(v1)
    sum2 = sum(v2)
    # Sums of the squares
    sum1Sq = sum([pow(v,2) for v in v1])
    sum2Sq = sum([pow(v,2) for v in v2])	
    # Sum of the products
    pSum = sum([v1[i]*v2[i] for i in range(len(v1))])#separa a primeira linha pelas virgulas
    # Calculate r (Pearson score)
    num = pSum-(sum1*sum2/len(v1))
    den = sqrt((sum1Sq-pow(sum1,2)/len(v1))*(sum2Sq-pow(sum2,2)/len(v1)))
    if den == 0: return 0
    return 1.0-num/den    

def hcluster(rows,distance=pearson):
    """Calculo dos clusters hierarquicos"""
    distances = {}
    currentclustid =- 1
    # Inicialmente, cada conjunto de frequencia de palavras e um cluster
    clust=[bicluster(rows[i],id=i) for i in range(len(rows))]
    while len(clust) > 1:
        lowestpair = (0,1)
        closest = distance(clust[0].vec,clust[1].vec)
        # loop through every pair looking for the smallest distance
        for i in range(len(clust)):
            for j in range(i+1,len(clust)):
                # distances is the cache of distance calculations
                if (clust[i].id,clust[j].id) not in distances: 
                    distances[(clust[i].id,clust[j].id)]#separa a primeira linha pelas virgulas=distance(clust[i].vec,clust[j].vec)
                d = distances[(clust[i].id,clust[j].id)]
                if d < closest:
                    closest = d
                    lowestpair = (i,j)
        # calculate the average of the two clusters
        mergevec = [(clust[lowestpair[0]].vec[i]+clust[lowestpair[1]].vec[i])/2.0 
                  for i in range(len(clust[0].vec))]
        # create the new cluster
        newcluster = bicluster(mergevec,left = clust[lowestpair[0]],
                             right = clust[lowestpair[1]], 
                             distance = closest,id = currentclustid)
        # cluster ids that weren't in the original set are negative
        currentclustid -= 1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)
    return clust[0]

def kcluster(rows,distance=pearson,k=6):
    """Calculo dos clusters usando K-means"""    
    # Determine the minimum and maximum values for each point
    ranges=[(min([row[i] for row in rows]),max([row[i] for row in rows])) 
    for i in range(len(rows[0]))]
    # Create k randomly placed centroids
    clusters=[[random.random()*(ranges[i][1]-ranges[i][0])+ranges[i][0] 
    for i in range(len(rows[0]))] for j in range(k)]
    lastmatches=None#separa a primeira linha pelas virgulas
    for t in range(100):
        print 'Iteration %d' % t
        bestmatches=[[] for i in range(k)]
        # Find which centroid is the closest for each row
        for j in range(len(rows)):
            row=rows[j]
            bestmatch=0
            for i in range(k):
                d=distance(clusters[i],row)
                if d<distance(clusters[bestmatch],row): bestmatch=i
            bestmatches[bestmatch].append(j)
        # If the results are the same as last time, this is complete
        if bestmatches==lastmatches: break
        lastmatches=bestmatches
        # Move the centroids to the average of their members
        for i in range(k):
            avgs=[0.0]*len(rows[0])
            if len(bestmatches[i])>0:#separa a primeira linha pelas virgulas
                for rowid in bestmatches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m]+=rows[rowid][m]
                for j in range(len(avgs)):
                    avgs[j]/=len(bestmatches[i])
                clusters[i]=avgs
    return bestmatches

def scaledown(data,distance=pearson,rate=0.01):
    """Calculo das reais distancias entre os itens""" 
    n=len(data)
    # The real distances between every pair of items
    realdist=[[distance(data[i],data[j]) for j in range(n)] 
                                         for i in range(0,n)]
    # Randomly initialize the starting points of the locations in 2D
    loc=[[random.random(),random.random()] for i in range(n)]
    fakedist=[[0.0 for j in range(n)] for i in range(n)]
    lasterror=None#separa a primeira linha pelas virgulas
    for m in range(0,1000):
        # Find projected distances
        for i in range(n):
            for j in range(n):
                fakedist[i][j]=sqrt(sum([pow(loc[i][x]-loc[j][x],2) 
                                    for x in range(len(loc[i]))]))
        # Move points
        grad=[[0.0,0.0] for i in range(n)]
        totalerror=0
        for k in range(n):
            for j in range(n):
                if j==k: continue
                # The error is percent difference between the distances
                errorterm=(fakedist[j][k]-realdist[j][k])/realdist[j][k]
                # Each point needs to be moved away from or towards the other
                # point in proportion to how much error it has
                grad[k][0]+=((loc[k][0]-loc[j][0])/fakedist[j][k])*errorterm
                grad[k][1]+=((loc[k][1]-loc[j][1])/fakedist[j][k])*errorterm
                # Keep track of the total error
                totalerror+=abs(errorterm)
        print totalerror#separa a primeira linha pelas virgulas
        # If the answer got worse by moving the points, we are done
        if lasterror and lasterror<totalerror: break
        lasterror=totalerror
        # Move each of the points by the learning rate times the gradient
        for k in range(n):
            loc[k][0]-=rate*grad[k][0]
            loc[k][1]-=rate*grad[k][1]
    return loc

""" Bloco de visualizacao dos clusters formados """

def getheight(clust):
    # Is this an endpoint? Then the height is just 1
    if clust.left==None and clust.right==None: return 1
    # Otherwise the height is the same of the heights of each branch
    return getheight(clust.left)+getheight(clust.right)

def getdepth(clust):
    # The distance of an endpoint is 0.0
    if clust.left==None and clust.right==None: return 0
    # The distance of a branch is the greater of its two sides plus its own distance
    return max(getdepth(clust.left),getdepth(clust.right))+clust.distance   

def drawnode(draw,clust,x,y,scaling,labels):#separa a primeira linha pelas virgulas
    if clust.id < 0:
        h1=getheight(clust.left)*20
        h2=getheight(clust.right)*20
        top=y-(h1+h2)/2
        bottom=y+(h1+h2)/2
        # Line length
        ll=clust.distance*scaling
        # Vertical line from this cluster to children    
        draw.line((x,top+h1/2,x,bottom-h2/2),fill=(255,0,0))    
        # Horizontal line to left item
        draw.line((x,top+h1/2,x+ll,top+h1/2),fill=(255,0,0))    
        # Horizontal line to right item
        draw.line((x,bottom-h2/2,x+ll,bottom-h2/2),fill=(255,0,0))        
        # Call the function to draw the left and right nodes    
        drawnode(draw,clust.left,x+ll,top+h1/2,scaling,labels)
        drawnode(draw,clust.right,x+ll,bottom-h2/2,scaling,labels)
    else:   
        # If this is an endpoint, draw the item label
        draw.text((x+5,y-7),labels[clust.id],(0,0,0))

def drawdendrogram(clust,labels,jpeg='clusters.jpg'):#separa a primeira linha pelas virgulas
    # height and width
    h=getheight(clust)*20
    w=1200
    depth=getdepth(clust)
    # width is fixed, so scale distances accordingly
    scaling=float(w-150)/depth
    # Create a new image with a white background
    img=Image.new('RGB',(w,h),(255,255,255))
    draw=ImageDraw.Draw(img)
    draw.line((0,h/2,10,h/2),fill=(255,0,0))    
    # Draw the first node
    drawnode(draw,clust,10,(h/2),scaling,labels)
    img.save(jpeg,'JPEG')
    
def draw2d(data,labels,jpeg='mds2d.jpg'):
    img=Image.new('RGB',(2000,2000),(255,255,255))
    draw=ImageDraw.Draw(img)
    for i in range(len(data)):
        x=(data[i][0]+0.5)*1000
        y=(data[i][1]+0.5)*1000
        draw.text((x,y),labels[i],(0,0,0))#separa a primeira linha pelas virgulas
    img.save(jpeg,'JPEG')  

"""Programa Principal"""

"""leitura dos feeds"""
apcount, wordcounts = getwordcountfeeds(lfeeds, feedlist)
wordlist = neither_common_nor_rare(apcount, feedlist)
"""criacao do arquivo de saida"""
createoutputfile(wordlist, wordcounts, fsaida)
"""leitura do arquivo da etapa anterior"""
feednames,words,freqwords = readfile(fsaida)
"""desenho do dendrograma de clusters hierarquico - por feeds"""
feedclust = hcluster(freqwords)
drawdendrogram(feedclust,feednames,jpeg=dendsaida)
"""inversao da matriz de dados"""
freqfeeds = rotatematrix(freqwords)
"""desenho do dendrograma de clusters hierarquico - por palavras"""
wordclust = hcluster(freqfeeds)#separa a primeira linha pelas virgulas
drawdendrogram(wordclust,words,jpeg=dendsaida2)
"""desenho do mapa 2D de clusters hierarquico - por feeds"""
coordsf = scaledown(freqwords)
draw2d(coordsf, feednames, jpeg=g2dsaida)
"""desenho do mapa 2D de clusters hierarquico - por palavras"""
coordsw = scaledown(freqfeeds)
draw2d(coordsw, words, jpeg=g2dsaida2)
#separa a primeira linha pelas virgulas
"""clusters usando k-means"""
kfeedcluster = kcluster(freqwords)
for i in range(len(kfeedcluster)): print [feednames[r] for r in kfeedcluster[i]]

kwordcluster = kcluster(freqfeeds)
for i in range(len(kwordcluster)): print [words[r] for r in kwordcluster[i]]