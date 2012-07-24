#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Mestrado em Modelagem Matematica da Informacao
Master Program - Mathematical Modeling of Information

Disciplina: Modelagem e Mineracao de Dados
Course: Data Mining and Modeling

Professor: Renato Rocha Souza
Topic: Filtering feeds and Documents (class #7)

Information on the Python Packages used:
http://docs.python.org/library/sqlite3.html
http://docs.python.org/library/re.html
http://www.feedparser.org/
'''

import re
import math
import feedparser
from sqlite3 import dbapi2 as sqlite

'''Specifying the path to the files'''

datapath = "/home/rsouza/Documentos/Git/MMD/datasets/"
outputs = "/home/rsouza/Documentos/outputs/"

dbfile1 = "treino.db"
dbfile2 = "treinoblogs.db"
outblog = "blogoutputrss.xml"

db_teste = (outputs+dbfile1)
db_blog = (outputs+dbfile2)
rssblogoutput = (outputs+outblog)
usedb = True #False

'''First block of functions: feature extraction'''

def getwords(doc):
    '''Remove the HTML tags and cleans the feeds files;splits the sentences 
    by the non alpha characters and converts all words to lowercase.
    Ignores bigger and too small words'''
    print('Documento -->  {}'.format(doc))
    splitter=re.compile('\\W*')
    words=[s.lower() for s in splitter.split(doc) if len(s)>2 and len(s)<20]
    return dict([(w,1) for w in words])
    
def entryfeatures(entry):
    '''Used when our features are not documents, but feeds rss'''
    splitter=re.compile('\\W*')
    f={}
    # Extract title words
    titlewords=[s.lower() for s in splitter.split(entry['title']) 
                if len(s)>2 and len(s)<20]
    for w in titlewords: f['Title:'+w]=1
    # Extract summary words
    summarywords=[s.lower() for s in splitter.split(entry['summary']) 
                if len(s)>2 and len(s)<20]
    # Count lowercase words
    uc=0
    for i in range(len(summarywords)):
        w=summarywords[i]
        f[w]=1
        if w.isupper(): uc+=1
        # Features are words in the feed summary
        if i<len(summarywords)-1:
            twowords=' '.join(summarywords[i:i+1])
            f[twowords]=1
    # Save publisher information
    f['Publisher:'+entry['publisher']]=1
    # Too many uppercase words are indicated
    if float(uc)/len(summarywords)>0.3: f['MAIUSCULAS']=1
    return f

'''Second block of functions: classification'''

class classifier:
    ''' Represents the classifier, storing what's learnt from training.
    fc saves the combination words/categories {'word': {'bad': 3, 'good': 2}}
    and cc is a dictionary that stores the number of times a category was used
    {'bad': 3, 'good': 2}. Will be used when no DB is used.
    Getfeatures is the feature extraction function to be used'''
    def __init__(self,getfeatures,filename=None):
        self.fc={}
        self.cc={}
        self.getfeatures=getfeatures 
    
    def setdb(self,dbfile):
        '''When using a database and not dictionaries, to persist the information
        across sessions'''
        self.con=sqlite.connect(dbfile)    
        self.con.execute('create table if not exists fc(feature,category,count)')
        self.con.execute('create table if not exists cc(category,count)')

    def fcount(self,f,cat):
        '''Returns the number of times a feature appears in a category'''
        if not usedb:
            if f in self.fc and cat in self.fc[f]: return float(self.fc[f][cat])
            else: return 0
        else:
            res=self.con.execute('''select count from fc where feature="{}" 
                                and category="{}"'''.format(f,cat)).fetchone()
            if res==None: return 0
            else: return float(res[0])

    def incf(self,f,cat):
        '''Creates a feature/category pair if not exists, or increase the number
        if feature exists in a category'''
        if not usedb:
            self.fc.setdefault(f,{})
            self.fc[f].setdefault(cat,0)
            self.fc[f][cat]+=1
        else:
            count=self.fcount(f,cat)
            if count==0:
                self.con.execute('insert into fc values ("{}","{}",1)'.format(f,cat))
            else:
                self.con.execute('''update fc set count={} where feature="{}" 
                                and category="{}"'''.format(count+1,f,cat)) 

    def incc(self,cat):
        '''Increases the number of occurrences of a category'''
        if not usedb:
            self.cc.setdefault(cat,0)
            self.cc[cat]+=1        
        else:
            count=self.catcount(cat)
            if count==0:
                self.con.execute('insert into cc values ("{}",1)'.format(cat))
            else:
                self.con.execute('''update cc set count={} where 
                                category="{}"'''.format(count+1,cat))    

    def catcount(self,cat):
        '''Counts the numer of itens in a category'''
        if not usedb:
            if cat in self.cc: return float(self.cc[cat])
            else: return 0
        else:
            res=self.con.execute('''select count from cc where category="{}"
                                '''.format(cat)).fetchone()
            if res==None: return 0
            else: return float(res[0])

    def categories(self):
        '''Lists all the categories'''        
        if not usedb: return self.cc.keys()
        else:
            cur=self.con.execute('select category from cc');
            return [d[0] for d in cur]

    def totalcount(self):
        ''' Returns the total numer of itens'''
        if not usedb: return sum(self.cc.values())
        else:
            res=self.con.execute('select sum(count) from cc').fetchone();
            if res==None: return 0
            else: return res[0]

    def train(self,item,cat):
        '''Receives an item (bag of features) and a classification, and increases
        the relative number of this classifications for all the features'''
        features=self.getfeatures(item)
        for f in features:
            self.incf(f,cat)
        self.incc(cat)
        if usedb: self.con.commit()

    def fprob(self,f,cat):
        '''Calculates the probability of a feature to be within a category'''
        if self.catcount(cat)==0: return 0
        return self.fcount(f,cat)/self.catcount(cat)

    def weightedprob(self,f,cat,prf,weight=1.0,ap=0.5):
        '''Calculates the probability of a feature to appear in a certain category
        as fprob does, but assuming an initial value and changing according to 
        the training. That minimizes the effect of a rare word to be classified
        erroneously'''
        basicprob=prf(f,cat)
        totals=sum([self.fcount(f,c) for c in self.categories()])
        bp=((weight*ap)+(totals*basicprob))/(weight+totals)
        return bp


class naivebayes(classifier):
    '''Extends classifier class overiding __init__ and adding specific functions
    to classify documents using naive bayes'''
    
    def __init__(self,getfeatures):
        classifier.__init__(self,getfeatures)
        self.thresholds={}
        
    def docprob(self,item,cat):
        '''Calculates the probability of a document to be within a given
        category multiplying all the features probabilities to be in this category'''
        features=self.getfeatures(item)
        p=1
        for f in features: p*=self.weightedprob(f,cat,self.fprob)
        return p

    def prob(self,item,cat):
        catprob=self.catcount(cat)/self.totalcount()
        docprob=self.docprob(item,cat)
        return docprob*catprob

    def setthreshold(self,cat,t):
        self.thresholds[cat]=t

    def getthreshold(self,cat):
        if cat not in self.thresholds: return 1.0
        return self.thresholds[cat]

    def classify(self,item,default=None):
        '''Finds the most probably category to classify'''        
        probs={}
        max=0.0
        for cat in self.categories():
            probs[cat]=self.prob(item,cat)
            if probs[cat]>max: 
                max=probs[cat]
                best=cat
        # Assegura-se que a probabilidade excede o limiar minimo estabelecido
        # entre a categoria escolhida a proxima categoria com maior probabilidade.
        # Caso negativo, retorna a categoria default (None ou Unknown, neste caso)
        for cat in probs:
            if cat==best: continue
            if probs[cat]*self.getthreshold(best)>probs[best]: return default
        return best

class fisherclassifier(classifier):
    '''Extends classifier class overiding __init__ and adding specific functions
    to classify documents using fisher method'''

    def __init__(self,getfeatures):
        classifier.__init__(self,getfeatures)
        self.minimums={}
    
    def cprob(self,f,cat):
        '''Returns the frequency of the feature in a category divided
        by the frequency in all categories'''
        clf=self.fprob(f,cat)
        if clf==0: return 0
        freqsum=sum([self.fprob(f,c) for c in self.categories()])
        p=clf/(freqsum)
        return p

    def invchi2(self,chi, df):
        m = chi / 2.0
        sum = term = math.exp(-m)
        for i in range(1, df//2):
            term *= m / i
            sum += term
        return min(sum, 1.0)

    def fisherprob(self,item,cat):
        '''Multipy all the categories, applies the natural log
        and uses the inverse chi2 to calculate probabilty'''
        p=1
        features=self.getfeatures(item)
        for f in features:
            p*=(self.weightedprob(f,cat,self.cprob))
        fscore=-2*math.log(p)
        return self.invchi2(fscore,len(features)*2)

    def setminimum(self,cat,min):
        self.minimums[cat]=min

    def getminimum(self,cat):
        if cat not in self.minimums: return 0
        return self.minimums[cat]

    def classify(self,item,default=None):
        '''Applies fisher to all categories to find the best result'''
        best=default
        max=0.0
        for c in self.categories():
            p=self.fisherprob(item,c)
            # Assegurando-se que esta excede o minimo estabelecido
            if p>self.getminimum(c) and p>max:
                best=c
                max=p
        return best

'''Third block of functions: reading files or feeds'''

def blogread(assunto,classifier): #(feed,classifier) -->caso fosse arquivo e nao web
    """Recebe uma url de um feed rss e classifica as entradas. Pode ler direto
    da web ou receber um arquivo rss xml como entrada - linhas comentadas"""
    # Recebe as entradas do feed e itera em cada uma
    url='http://www.google.com/search?q={}&hl=pt-BR&tbm=blg&output=rss'.format(assunto)
    #f=feedparser.parse(feed) #-->caso fosse arquivo e nao web
    f=feedparser.parse(url)
    for entry in f['entries']:
        print
        print '-----'
        # Exibe o conteudo de uma entrada do feed
        print 'Title:     '+entry['title'].encode('utf-8')
        print 'Publisher: '+entry['publisher'].encode('utf-8')
        print
        print entry['summary'].encode('utf-8')
        # Combina as partes em um texto unico para ser classificado
        fulltext='%s\n%s\n%s' % (entry['title'],entry['publisher'],entry['summary'])
        # Exibe o melhor palpite para a categoria em questao
        print 'Guess: '+str(classifier.classify(entry))
        # Pede ao usuario para especificar a categoria correta
        # e treina o classificador nesta categoria
        cl=raw_input('Enter category: ').lower()
        classifier.train(entry,cl)

'''Fourth block of functions: tests and demonstrations'''

def sampletrain(cl):
    """Algumas sentencas para prover um treinamento inicial
    dos classificadores"""
    cl.train('Nobody owns the water.','good')
    cl.train('the quick rabbit jumps fences','good')
    cl.train('buy pharmaceuticals now','bad')
    cl.train('make quick money at the online casino','bad')
    cl.train('the quick brown fox jumps','good')

def probabilidades_palavras():
    cl = classifier(getwords)
    sampletrain(cl)
    print 'Em quantas frases "quick" --> bom:' , cl.fcount('quick','good')
    print 'Em quantas frases "quick" --> ruim:' , cl.fcount('quick','bad')
    print 'A probabilidade de ter "quick" dado que eh bom:',cl.fprob('quick','good')
    print 'A probabilidade de ter "money" dado que eh bom:'
    print cl.fprob('money','good'), 'usando fprob'
    print 'A probabilidade ponderada de ter "money" dado que eh bom:'
    print cl.weightedprob('money','good',cl.fprob), 'usando weightedprob'
    print 'treinando de novo com os mesmos documentos. . . . . . .'
    sampletrain(cl)
    print 'A probabilidade de ter "money" dado que eh bom:'
    print cl.fprob('money','good'), 'usando fprob'
    print 'A probabilidade ponderada de ter "money" dado que eh bom:'
    print cl.weightedprob('money','good',cl.fprob), 'usando weightedprob'

def probabilidades_documentos_bayes():
    cl = naivebayes(getwords)
    sampletrain(cl)
    #print 'A probabilidade de ser bom dado que: ',cl.prob('quick rabbit','good')
    #print 'A probabilidade de ser ruim dado que: ',cl.prob('quick rabbit','bad')
    print 'A classificacao prevista para  "quick rabbit" '
    print cl.classify('quick rabbit', default = 'unknown')
    print 'A classificacao prevista para  "quick money" '
    print cl.classify('quick money', default = 'unknown')
    print 'Aumentando o limiar para que um documento seja considerado ruim...'
    cl.setthreshold('bad',3.0)
    print 'A classificacao prevista para  "quick money" '
    print cl.classify('quick money', default = 'unknown')
    print 'rodando os dados de treinamento mais 10 vezes...'
    for i in range(10): sampletrain(cl)
    print 'A classificacao prevista para  "quick money" ' 
    print cl.classify('quick money', default = 'unknown')

def probabilidades_palavras_fisher():
    cl = fisherclassifier(getwords)
    sampletrain(cl)
    print 'A probabilidade de ter "quick" dado que eh bom:'
    print cl.cprob('quick', 'good')
    print 'A probabilidade de ter "money" dado que eh bom:'
    print cl.cprob('money', 'bad')
    print 'A probabilidade ponderada de ter "money" dado que eh ruim:'
    print cl.weightedprob('money','bad',cl.cprob), 'usando weightedprob'

def probabilidades_documentos_fisher():
    cl = fisherclassifier(getwords)
    sampletrain(cl)
    print 'A classificacao prevista para  "quick rabbit" '
    print cl.classify('quick rabbit')
    print 'A classificacao prevista para  "quick money" '
    print cl.classify('quick money')
    print 'Aumentando o limiar para que um documento seja considerado ruim...'
    cl.setminimum('bad',0.8)
    print 'A classificacao prevista para  "quick money" '
    print cl.classify('quick money')
    print 'Diminuindo o limiar para que um documento seja considerado ruim...'
    cl.setminimum('bad',0.4)
    print 'A classificacao prevista para  "quick money" ' 
    print cl.classify('quick money', default = 'unknown')

def usando_dbase():
    cl = fisherclassifier(getwords)
    cl.setdb(db_teste)
    sampletrain(cl) #treinando usando fisher
    cl2 = naivebayes(getwords)
    cl2.setdb(db_teste) #usando o treino de fisher para classificar com bayes
    print cl.classify('quick money')

def classifica_blogs(assunto):
    cl = fisherclassifier(entryfeatures) #usa entryfeatures ao inves de getwords
    cl.setdb(db_blog)
    #blogread(rssblogoutput,cl) #lendo o feed gravado em um arquivo
    blogread(assunto,cl)    
    print "Lista de categorias usadas:"
    for c in cl.categories(): print c
    print "Teste agora as probabilidades com cprob('<palavra>,<categoria>')"
    print "Ou as probabilidades com fprob('<categoria>','<palavra>')"
    return cl
    
if __name__ == '__main__':
    #probabilidades_palavras()
    #probabilidades_documentos_bayes()
    #probabilidades_palavras_fisher()
    #probabilidades_documentos_fisher()
    #usando_dbase()
    clb = classifica_blogs('fgv')
