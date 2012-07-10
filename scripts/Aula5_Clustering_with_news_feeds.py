#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Mestrado em Modelagem Matematica da Informacao
Master Program - Mathematical Modeling of Information

Disciplina: Modelagem e Mineracao de Dados
Course: Data Mining and Modeling

Professor: Renato Rocha Souza
Topic: Clustering news feeds (class #5)

Information on the Python Packages used:
http://www.feedparser.org/
http://docs.python.org/library/re.html
http://www.pythonware.com/library/pil/handbook/index.htm
'''

import feedparser
import re
from PIL import Image,ImageDraw
from math import sqrt
import random

'''Specifying the path to the files'''
datapath = "/home/rsouza/Documentos/Git/MMD/datasets/"
outputs = "/home/rsouza/Documentos/outputs/"
dataset = "cotacoesbovespa.txt"

listafeeds = "ch05_feedlist.txt"
stopwords = "ch05_stopwords.txt"
saida = "output.txt"
dendrog1 = "feedclusters.jpg"
dendrog2 = "wordclusters.jpg"
g2d1 = "g2dfeeds.jpg"
g2d2 = "g2dwords.jpg"
lfeeds = (datapath+listafeeds)
lstopwords = (datapath+stopwords)
fsaida = (outputs+saida)
dendsaida = (outputs+dendrog1)
dendsaida2 = (outputs+dendrog2)
g2dsaida = (outputs+g2d1)
g2dsaida2 = (outputs+g2d2)


'''First block of functions - reading and processing the words in blog feeds'''

def getwords(html):
    '''Remove the HTML tags and cleans the feeds files
    splits the sentences by the non alpha characters
    and converts all words to lowercase'''
    txt = re.compile(r'<[^>]+>').sub('',html)
    words = re.compile(r'[^A-Z^a-z]+').split(txt)
    return [word.lower() for word in words if word!='']

def getwordcounts(url):
    '''Parse the feed and returns a dictionary with word counts
    for each feed entry, it searches for summary ou description
    (optionally) eliminating the stopwords. Cleans feeds with function getwords'''
    d = feedparser.parse(url)
    wc = {}
    for entry in d.entries:
        if 'summary' in entry:
            summary = entry.summary
        else:
            summary = entry.description
        words = getwords(entry.title+' '+summary)
        stoplist = file(lstopwords).readlines()
        stoplist = [word.strip() for word in stoplist]
        words = [word for word in words if word not in stoplist]
        for word in words:
            wc.setdefault(word,0) #setting default values to zero
            wc[word] += 1 # incrementing every time it occurs
    return d.feed.title,wc

def getwordcountfeeds(lfeeds, feedlist):
    '''tries to access the feed using the function getwordcounts and returns
    two dictionaries: the blogs in which a word occur, and the times a word appear in a blog'''    
    apcount = {}
    wordcounts = {}
    for feedurl in feedlist:
        try:
            title,wc = getwordcounts(feedurl)
            wordcounts[title] = wc
            for word,count in wc.items():
                apcount.setdefault(word,0)
                if count > 1:
                    apcount[word] += 1
        except:
            print('Failure trying to access feed {}').format(feedurl)
    return apcount, wordcounts

def neither_common_nor_rare(apcount, feedlist):
    '''Optional function, to filter unwanted words (very common or very rare)'''
    wordlist = []
    for w,bc in apcount.items():
        frac = float(bc)/len(feedlist)
        if frac > 0.1 and frac < 0.9: #ajustar estes parametros
            wordlist.append(w)
    return wordlist
    

'''Second block of functions - saving data files to persist data gathered
and retrieving the data saved for future analysis'''


def createoutputfile(wordlist, wordcounts, filename):
    '''Save name of feeds, words and its frequencies.
    Names the heads of the files and separate columns by <tabs>'''
    out = file(filename,'w')
    out.write('Feed')
    for word in wordlist: out.write('\t%s' % word)
    out.write('\n')
    for feed,wc in wordcounts.items():
        print 'Processado o feed: ', feed 
        out.write(feed)
        for word in wordlist:
            if word in wc: out.write('\t%d' % wc[word])
            else: out.write('\t0')
        out.write('\n')

def readfile(filename):
    '''Read the file and formats data'''
    lines = [line for line in file(filename)]
    colnames = lines[0].strip().split('\t')[1:]
    rownames = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('\t')
        rownames.append(p[0])
        data.append([float(x) for x in p[1:]])
    return rownames,colnames,data

def rotatematrix(data):
    newdata = []
    for i in range(len(data[0])):
        newrow = [data[j][i] for j in range(len(data))]
        newdata.append(newrow)#separa a primeira linha pelas virgulas
    return newdata

'''Third block of functions - calculating the clusters'''

class bicluster:
    '''representing a hierarchical partioned cluster'''
    def __init__(self,vec,left = None, right = None,distance = 0.0,id = None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance

def pearson(v1,v2):
    '''One of the many algorithms to calculate correlation
    as an alternative to euclidean distance'''
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
    '''Calculating hierarchical clusters'''
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
                    distances[(clust[i].id,clust[j].id)]=distance(clust[i].vec,clust[j].vec)
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
    '''Calculating clusters using K-means'''
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
    '''Calculating the actual distances among the items'''
    n=len(data)
    # The real distances between every pair of items
    realdist=[[distance(data[i],data[j]) for j in range(n)] 
                                         for i in range(0,n)]
    # Randomly initialize the starting points of the locations in 2D
    loc=[[random.random(),random.random()] for i in range(n)]
    fakedist=[[0.0 for j in range(n)] for i in range(n)]
    lasterror=None
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

'''Fourth block of functions - visualizing the clusters'''

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

def drawnode(draw,clust,x,y,scaling,labels):
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

def drawdendrogram(clust,labels,jpeg='clusters.jpg'):
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
        draw.text((x,y),labels[i],(0,0,0))
    img.save(jpeg,'JPEG')  




if __name__ == '__main__':
    #reads the list of blogs to analyze
    feedlist=[line for line in file(lfeeds)]
    apcount, wordcounts = getwordcountfeeds(lfeeds, feedlist)
    wordlist = neither_common_nor_rare(apcount, feedlist)
    createoutputfile(wordlist, wordcounts, fsaida)
    feednames,words,freqwords = readfile(fsaida)

    #drawing the (hierarchical) dendrogram by feeds
    feedclust = hcluster(freqwords)
    drawdendrogram(feedclust,feednames,jpeg=dendsaida)

    #inverting the data matrix
    #drawing the (hierarchical) dendrogram by words
    freqfeeds = rotatematrix(freqwords)
    wordclust = hcluster(freqfeeds) 
    drawdendrogram(wordclust,words,jpeg=dendsaida2)

    #drawing the 2D map by feeds
    coordsf = scaledown(freqwords)
    draw2d(coordsf, feednames, jpeg=g2dsaida)
    
    #drawing the 2D map by words
    coordsw = scaledown(freqfeeds)
    draw2d(coordsw, words, jpeg=g2dsaida2)
    
    #cluster feeds and words usando k-means - textual output
    kfeedcluster = kcluster(freqwords)
    for i in range(len(kfeedcluster)): print [feednames[r] for r in kfeedcluster[i]]
    kwordcluster = kcluster(freqfeeds)
    for i in range(len(kwordcluster)): print [words[r] for r in kwordcluster[i]]