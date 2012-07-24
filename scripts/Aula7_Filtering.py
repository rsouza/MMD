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

'''First block of functions: feature extraction'''

def getwords(doc):
    '''Remove the HTML tags and cleans the feeds files;splits the sentences 
    by the non alpha characters and converts all words to lowercase.
    Ignores bigger and too small words'''
    #print('Documento -->  {}'.format(doc))
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
    def __init__(self, getfeatures, filename=None, usedb=False):
        self.fc={}
        self.cc={}
        self.getfeatures = getfeatures
        self.usedb = usedb
    
    def setdb(self,dbfile):
        '''When using a database and not dictionaries, to persist the information
        across sessions'''
        self.con = sqlite.connect(dbfile)    
        self.con.execute('create table if not exists fc(feature,category,count)')
        self.con.execute('create table if not exists cc(category,count)')

    def fcount(self,f,cat):
        '''Returns the number of times a feature appears in a category'''
        if not self.usedb:
            if f in self.fc and cat in self.fc[f]: 
                return float(self.fc[f][cat])
            else: 
                return 0
        else:
            query = 'select count from fc where feature="{}" and category="{}"'
            res = self.con.execute(query.format(f,cat)).fetchone()
            if res == None: 
                return 0
            else: 
                return float(res[0])

    def incf(self,f,cat):
        '''Creates a feature/category pair if not exists, or increase the number
        if feature exists in a category'''
        if not self.usedb:
            self.fc.setdefault(f,{})
            self.fc[f].setdefault(cat,0)
            self.fc[f][cat] += 1
        else:
            count=self.fcount(f,cat)
            if count == 0:
                self.con.execute('insert into fc values ("{}","{}",1)'.format(f,cat))
            else:
                query = 'update fc set count={} where feature="{}" and category="{}"'
                self.con.execute(query.format(count+1,f,cat)) 

    def incc(self,cat):
        '''Increases the number of occurrences of a category'''
        if not self.usedb:
            self.cc.setdefault(cat,0)
            self.cc[cat] += 1        
        else:
            count=self.catcount(cat)
            if count == 0:
                self.con.execute('insert into cc values ("{}",1)'.format(cat))
            else:
                query = 'update cc set count={} where category="{}"'
                self.con.execute(query.format(count+1,cat))    

    def catcount(self,cat):
        '''Counts the numer of itens in a category'''
        if not self.usedb:
            if cat in self.cc:
                return float(self.cc[cat])
            else:
                return 0
        else:
            query = 'select count from cc where category="{}"'
            res=self.con.execute(query.format(cat)).fetchone()
            if res == None:
                return 0
            else:
                return float(res[0])

    def categories(self):
        '''Lists all the categories'''        
        if not self.usedb: return self.cc.keys()
        else:
            cur=self.con.execute('select category from cc');
            return [d[0] for d in cur]

    def totalcount(self):
        ''' Returns the total numer of itens'''
        if not self.usedb: return sum(self.cc.values())
        else:
            res=self.con.execute('select sum(count) from cc').fetchone();
            if res==None: return 0
            else: return res[0]

    def train(self,item,cat):
        '''Receives an item (a bag of features) and a category, and increases
        the relative number of this category for all the features'''
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
    '''Extends classifier class overriding __init__ and adding specific functions
    to classify documents using naive bayes'''
    
    def __init__(self, getfeatures, usedb=False):
        classifier.__init__(self,getfeatures)
        self.thresholds = {}
        self.usedb = usedb
        
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

    def classify(self, item, default=None):
        '''Finds the most probably category to be set, and apply this
        classification, given that it satisfies a minimum threshold, compared
        to the second best category to classify; otherwise sets to "None"'''        
        probs = {}
        maximum = 0.0
        best = None
        for cat in self.categories():
            probs[cat] = self.prob(item, cat)
            if probs[cat] > maximum: 
                maximum = probs[cat]
                best = cat
        for cat in probs:
            if cat == best:
                continue
            if probs[cat]*self.getthreshold(best) > probs[best]: 
                return default
        return best

class fisherclassifier(classifier):
    '''Extends classifier class overriding __init__ and adding specific functions
    to classify documents using fisher method'''

    def __init__(self,getfeatures, usedb=False):
        classifier.__init__(self, getfeatures)
        self.minimums = {}
        self.usedb = usedb
        
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
        p = 1
        features = self.getfeatures(item)
        for f in features:
            p *= (self.weightedprob(f,cat,self.cprob))
        fscore =- 2*math.log(p)
        return self.invchi2(fscore,len(features)*2)

    def setminimum(self,cat, minimum):
        self.minimums[cat] = minimum

    def getminimum(self,cat):
        if cat not in self.minimums: return 0
        return self.minimums[cat]

    def classify(self, item, default=None):
        '''Applies fisher to all categories to find the best result, given 
        that it satisfies a minimum threshold, otherwise sets to "None"'''
        best = default
        maximum = 0.0
        for c in self.categories():
            p = self.fisherprob(item,c)
            if p>self.getminimum(c) and p > maximum:
                best = c
                maximum = p
        return best

'''Third block of functions: reading files or searching for feeds'''

def blogread(file_or_subject, classifier, search=True):
    '''Receives an url to search Google for blogs in a given subject, or a 
    rss xml file with saved feeds. Tries to classify the entries'''
    if search:
        generic = 'http://www.google.com/search?q={}&hl=pt-BR&tbm=blg&output=rss'
        url = generic.format(file_or_subject)
        f = feedparser.parse(url)
    else:
        f = feedparser.parse(file_or_subject)
    for entry in f['entries']:
        fulltext='{}\n{}\n{}'.format(entry['title'],entry['publisher'],entry['summary'])        
        print('\n-----')
        print('Title:     '+entry['title'].encode('utf-8'))
        print('Publisher: '+entry['publisher'].encode('utf-8'))
        print()        
        print(entry['summary'].encode('utf-8'))
        guess = classifier.classify(entry)
        print('Suggested: {}'.format(guess))
        cl = raw_input('Enter category or press <enter> to accept suggestion: ').lower()
        if cl == ''.strip() and guess:
            cl = guess
        print('Category "{}" chosen'.format(cl))
        classifier.train(entry,cl)
        
'''Fourth block of functions: instantiating and training classifiers'''

def sampletrain(cl):
    print('Running sampletrain to train the classifier...')
    cl.train('Nobody owns the water.','good')
    cl.train('the quick rabbit jumps fences','good')
    cl.train('buy pharmaceuticals now','bad')
    cl.train('make quick money at the online casino','bad')
    cl.train('the quick brown fox jumps','good')

def probabilidades_palavras():
    cl = classifier(getwords)
    print('\n')    
    sampletrain(cl)
    
    print('How many times "quick" --> "good": {}'.format(cl.fcount('quick','good')))
    print('How many times "quick" --> "bad": {}'.format(cl.fcount('quick','bad')))
    print('\nProbability of "quick" given that "good": {}'.format(cl.fprob('quick','good')))
    print('Probability of "money" given that "good" (fprob): {}'.format(cl.fprob('money','good')))
    print('Weighted probability of "money" given that "good" (weightedprob): {}'.format(cl.weightedprob('money','good',cl.fprob)))

    print('\nTraining again with the same documents...\n')
    sampletrain(cl)

    print('\nProbability of "money" given that "good" (fprob): {}'.format(cl.fprob('money','good')))
    print('Weighted probability of "money" given that "good" (weightedprob): {}\n'.format(cl.weightedprob('money','good',cl.fprob)))

def probabilidades_documentos_bayes():
    cl = naivebayes(getwords)
    print('\n')    
    sampletrain(cl)
    
    print('Classifying "quick rabbit": {}'.format(cl.classify('quick rabbit', default='unknown')))
    print('Classifying "quick money": {}'.format(cl.classify('quick money', default='unknown')))
    
    print('\nSetting the threshold up...')
    cl.setthreshold('bad',3.0)

    print('Classifying "quick money": {}'.format(cl.classify('quick money', default='unknown')))
    
    print('\nTraining again with the same documents (10x)...')
    for i in range(10): sampletrain(cl)
    
    print('\nClassifying "quick money": {}'.format(cl.classify('quick money', default='unknown')))

def probabilidades_palavras_fisher():
    cl = fisherclassifier(getwords)
    print('\n')    
    sampletrain(cl)
    print('\n')      
    print('Probability of "quick" given that "good": {}'.format(cl.cprob('quick', 'good')))
    print('Probability of "money" given that "bad": {}'.format(cl.cprob('money', 'bad')))
    print('Weighted probability of  "money" given that "bad": {}'.format(cl.weightedprob('money','bad',cl.cprob)))

def probabilidades_documentos_fisher():
    cl = fisherclassifier(getwords)
    print('\n')    
    sampletrain(cl)

    print('Classifying "quick rabbit": {}'.format(cl.classify('quick rabbit')))
    print('Classifying "quick money": {}'.format(cl.classify('quick money')))
   
    print('\nSetting the threshold up...')
    cl.setminimum('bad',0.8)
    print('Classifying "quick money": {}'.format(cl.classify('quick money')))

    print('\nSetting the threshold down...')
    cl.setminimum('bad',0.4)
    print('Classifying "quick money": {}'.format(cl.classify('quick money')))

def using_db_example():
    '''Training with a classifier, persisting in a database
    using the training data to classify using another classifier'''
    print('\nInstantiating a fisher classifier...')
    cl = fisherclassifier(getwords, usedb=True)
    cl.setdb(db_teste)
    sampletrain(cl)
    print('\nInstantiating a naive bayes classifier...')    
    cl2 = naivebayes(getwords, usedb=True)
    cl2.setdb(db_teste)
    print('Classifying "quick money": {}'.format(cl.classify('quick money')))

def classifying_blogs(subject=''):
    '''Instantiating a new classifier using "entryfeatures" (for feeds)
    Creating the database for the persistance of training data
    Using blogread with searching feeds option - no file reading'''
    cl = fisherclassifier(entryfeatures, usedb=True)
    cl.setdb(db_blog)
    if not subject:
        subject = raw_input('\n\nPlease enter a subject to search for feeds: ').lower()
    blogread(subject, cl)    
    print('\nList of categories stored in the database:')
    for category in cl.categories(): 
        print(category)
    print('\n\nDo some tests now with:')
    print('cl.cprob(<category>,<word>)')
    print('cl.fprob(<word>,<category>)\n')

if __name__ == '__main__':
    probabilidades_palavras()
    probabilidades_documentos_bayes()
    probabilidades_palavras_fisher()
    probabilidades_documentos_fisher()
    using_db_example()
    #classifying_blogs('Dilma')



