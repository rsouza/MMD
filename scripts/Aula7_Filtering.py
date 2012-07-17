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
    """Separa as palavras por todos os caracteres nao alfabeticos, transforma em 
    minusculas e ignora palavras muito pequenas ou muito grandes.
    Retorna um dicionario com as palavras sem repeticao. A funcao getwords eh 
    adequada quando nossas features sao palavras. Estas podem ser, em outras 
    implementacoes, grupos de palavras, numero de maiusculas, ou outra 
    caracteristica qualquer para efeitos de classificacao"""
    #print 'Documento --> "',doc,'"'
    splitter=re.compile('\\W*')
    words=[s.lower() for s in splitter.split(doc) if len(s)>2 and len(s)<20]
    return dict([(w,1) for w in words])
    
def entryfeatures(entry):
    """Ao inves de lidar com documentos consttuidos de palavras, lida com 
    entradas de um feed no formato rss (um arquivo xml). A funcao entryfeatures
    eh adequada quando nossas features sao feeds rss"""
    splitter=re.compile('\\W*')
    f={}
    # Extrai as palavras do titulo e as marca como tal
    titlewords=[s.lower() for s in splitter.split(entry['title']) 
                if len(s)>2 and len(s)<20]
    for w in titlewords: f['Title:'+w]=1
    # Extrai as palavras do sumario
    summarywords=[s.lower() for s in splitter.split(entry['summary']) 
                if len(s)>2 and len(s)<20]
    # Conta as palavras que estao em maiusculo
    uc=0
    for i in range(len(summarywords)):
        w=summarywords[i]
        f[w]=1
        if w.isupper(): uc+=1
        # COnsidera pares de palavras no sumario como features
        if i<len(summarywords)-1:
            twowords=' '.join(summarywords[i:i+1])
            f[twowords]=1
    # Mantem o criador ou editor como uma unica palavra
    f['Publisher:'+entry['publisher']]=1
    # MAIUSCULAS se transforma em uma feature que indica muitas palavras maiusculas
    if float(uc)/len(summarywords)>0.3: f['MAIUSCULAS']=1
    return f

'''Second block of functions: classification'''

class classifier:
    """A classe representa o classificador, armazenando as informacoes
    aprendidas ate o momento. Sendo uma classe, pode ser instanciada
    para grupos diferentes e classificacoes distintas"""
    
    def __init__(self,getfeatures,filename=None):
        # fc guarda a contagem de combinacoes features/categorias
        # No caso de fatures = palavras, eh um dicionario
        # no formato {'palavra': {'ruim': 3, 'bom': 2}}
        self.fc={}
        # cc eh um dicionario que guarda o numero de vezes em que uma
        # categoria ex: {'ruim': 3, 'bom': 2}} foi usada.
        self.cc={}
        # fc e cc nao sao usados caso estejamos optando por persistir os
        #dados em um banco de dados (ver funcoes abaixo)        
        #getfeatures sera a funcao que extraira as features. Nesse exemplo, 
        #sera a funcao getwords, pois as features sao palavras
        self.getfeatures=getfeatures 
    
    def setdb(self,dbfile):
        """Caso estejamos trabalhando com um banco de dados para persistir
        (armazenar para as proximas sessoes) o treinamento realizado ate entao,
        usamos a funcao setdb para inicializar as tabelas"""
        self.con=sqlite.connect(dbfile)    
        self.con.execute('create table if not exists fc(feature,category,count)')
        self.con.execute('create table if not exists cc(category,count)')

    def fcount(self,f,cat):
        """Essa funcao retorna o numero de vezes que uma feature aparece em uma
        categoria. Podemos usar um dicionario ou um banco de dados"""
        if not usedb:
            if f in self.fc and cat in self.fc[f]: return float(self.fc[f][cat])
            else: return 0
        else:
            res=self.con.execute('select count from fc where feature="%s" and category="%s"' %(f,cat)).fetchone()
            if res==None: return 0
            else: return float(res[0])

    def incf(self,f,cat):
        """Essa funcao cria um par feature/categoria, caso nao exista, ou entao
        incrementa o numero de ocorrencias de uma feature em uma determinada
        categoria. Podemos usar um dicionario ou um banco de dados"""
        if not usedb:
            self.fc.setdefault(f,{})
            self.fc[f].setdefault(cat,0)
            self.fc[f][cat]+=1
        else:
            count=self.fcount(f,cat)
            if count==0:
                self.con.execute("insert into fc values ('%s','%s',1)" % (f,cat))
            else:
                self.con.execute("update fc set count=%d where feature='%s' and category='%s'" 
                                %(count+1,f,cat)) 

    def incc(self,cat):
        """Essa funcao incrementa o numero de ocorrencias de uma categoria.
        Podemos usar um dicionario ou um banco de dados"""
        if not usedb:
            self.cc.setdefault(cat,0)
            self.cc[cat]+=1        
        else:
            count=self.catcount(cat)
            if count==0:
                self.con.execute("insert into cc values ('%s',1)" % (cat))
            else:
                self.con.execute("update cc set count=%d where category='%s'"
                                %(count+1,cat))    

    def catcount(self,cat):
        """Essa funcao conta o numero de itens em uma categoria.
        Podemos usar um dicionario ou um banco de dados"""
        if not usedb:
            if cat in self.cc: return float(self.cc[cat])
            else: return 0
        else:
            res=self.con.execute('select count from cc where category="%s"'
                                %(cat)).fetchone()
            if res==None: return 0
            else: return float(res[0])

    def categories(self):
        """Essa funcao lista todas as categorias.
        Podemos usar um dicionario ou um banco de dados"""
        if not usedb: return self.cc.keys()
        else:
            cur=self.con.execute('select category from cc');
            return [d[0] for d in cur]

    def totalcount(self):
        """Essa funcao retorna o numero total de itens. 
        Podemos usar um dicionario ou um banco de dados"""
        if not usedb: return sum(self.cc.values())
        else:
            res=self.con.execute('select sum(count) from cc').fetchone();
            if res==None: return 0
            else: return res[0]

    def train(self,item,cat):
        """Essa funcao recebe um item (neste exemplo, um documento contendo 
        palavras, que sao as features e uma classificacao (ex:spam) e aumenta o
        numero relativo a aquela classificacao para cada feature (palavra, neste 
        exemplo) na nossa estrutura de armazenamento. Podemos usar um dicionario
        ou um banco de dados"""
        features=self.getfeatures(item)
        # Incrementa a contagem para cada item nesta categoria com a funcao incf
        for f in features:
            self.incf(f,cat)
        #Incrementa a contagem da categoria
        self.incc(cat)
        if usedb: self.con.commit()

    def fprob(self,f,cat):
        """Essa funcao calcula a probabilidade de uma feature aparecer em uma
        determinada categoria. Conta-se o numero de vezes que uma feature
        (palavra) aparece em uma categoria e divide-se pelo numero total de
        itens nesta categoria"""
        if self.catcount(cat)==0: return 0
        return self.fcount(f,cat)/self.catcount(cat)

    def weightedprob(self,f,cat,prf,weight=1.0,ap=0.5):
        """Essa funcao tambem calcula a probabilidade de uma feature aparecer em
        uma determinada categoria como faz fprob, mas enquanto fprob se baseia apenas
        no treinamento para determinar a probabilidade de uma feature aparecer em
        uma categoria, weightedprob comeca com um valor inicial e vai mudando de acordo
        com o treinamento. Isto impede que poucos documentos classificados de uma
        determinada maneira estabelecam a categoria de uma palavra de forma extrema"""
        # Calcula a probabilidade atual
        basicprob=prf(f,cat)
        # Conta o numero de vezes que a feature aparece em todas as categorias
        totals=sum([self.fcount(f,c) for c in self.categories()])
        # Calcula a probabilidade ponderada
        bp=((weight*ap)+(totals*basicprob))/(weight+totals)
        return bp


class naivebayes(classifier):
    """Estende a classe classifier, sobrepondo o metodo __init__
    e acrescentando as funcoes especificas para classificar documentos
    usando naive bayes"""
    
    def __init__(self,getfeatures):
        classifier.__init__(self,getfeatures)
        self.thresholds={}
        
    def docprob(self,item,cat):
        """Esta funcao calcula a probabilidade de um documento estar em uma
        categoria atraves da multiplicacao de todas as probabilidades de cada 
        uma das features (palavras, neste caso) do documento"""
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
        probs={}
        # Acha a categoria com maior probabilidade para classificacao
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
    """Estende a classe classifier, sobrepondo o metodo __init__
    e acrescentando as funcoes especificas para uma classificacao
    usando o metodo de fisher"""

    def __init__(self,getfeatures):
        classifier.__init__(self,getfeatures)
        self.minimums={}
    
    def cprob(self,f,cat):
        # A frequencia desta feature (palavra) nesta categoria    
        clf=self.fprob(f,cat)
        if clf==0: return 0
        #  A frequencia desta feature (palavra) em todas as categorias
        freqsum=sum([self.fprob(f,c) for c in self.categories()])
        # A probabilidade eh a frequencia nesta categoria dividido pela
        # frequencia em todas as categorias.
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
        # Multiplica todas as categorias
        p=1
        features=self.getfeatures(item)
        for f in features:
            p*=(self.weightedprob(f,cat,self.cprob))
        # Aplica o logaritmo natural e multiplica por -2
        fscore=-2*math.log(p)
        # Usa o inverso da funcao chi2 para chegar a probabilidade 
        return self.invchi2(fscore,len(features)*2)

    def setminimum(self,cat,min):
        self.minimums[cat]=min

    def getminimum(self,cat):
        if cat not in self.minimums: return 0
        return self.minimums[cat]

    def classify(self,item,default=None):
        # Aplica fisher em todas as categorias buscando pelo
        # melhor resultado
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
