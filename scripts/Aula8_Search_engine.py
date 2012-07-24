#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Mestrado em Modelagem Matematica da Informacao
Master Program - Mathematical Modeling of Information

Disciplina: Modelagem e Mineracao de Dados
Course: Data Mining and Modeling

Professor: Renato Rocha Souza
Topic: Search and ranking (class #8)

Information on the Python Packages used:
http://docs.python.org/library/sqlite3.html
http://www.crummy.com/software/BeautifulSoup/
http://docs.python.org/library/urlparse.html
http://nltk.org/
'''

import urllib2
from bs4 import BeautifulSoup
from urlparse import urljoin
from sqlite3 import dbapi2 as sqlite
import nltk

'''Specifying the path to the files'''

outputs = "/home/rsouza/Documentos/outputs/"

dbfile = "searchindex.sqlite"
db = (outputs+dbfile)
ignorewords={'the':1,'of':1,'to':1,'and':1,'a':1,'in':1,'is':1,'it':1}
stoplist_en = nltk.corpus.stopwords.words('english')
stoplist_pt = nltk.corpus.stopwords.words('portuguese')

'''First block of classes and functions: crawling'''

class crawler:
    def __init__(self,dbname):
        self.con=sqlite.connect(dbname)
        
    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    def createindextables(self):
        self.con.execute('create table urllist(url)')
        self.con.execute('create table wordlist(word)')
        self.con.execute('create table wordlocation(urlid,wordid,location)')
        self.con.execute('create table link(fromid integer,toid integer)')
        self.con.execute('create table linkwords(wordid,linkid)')
        self.con.execute('create index wordidx on wordlist(word)')
        self.con.execute('create index urlidx on urllist(url)')
        self.con.execute('create index wordurlidx on wordlocation(wordid)')
        self.con.execute('create index urltoidx on link(toid)')
        self.con.execute('create index urlfromidx on link(fromid)')
        self.dbcommit()

    def getentryid(self, table, field, value, createnew=True):
        '''Adds page ids to the database, if not present'''
        cur=self.con.execute("select rowid from {} where {}='{}'".format(table,field,value))
        res=cur.fetchone()
        if res == None:
            cur=self.con.execute("insert into {} ({}) values ('{}')".format(table,field,value))
            return cur.lastrowid
        else:
            return res[0] 

    def addtoindex(self,url,sopa):
        if self.isindexed(url): 
            print 'Pagina %s ja indexada...'%url
            return
        print 'Indexando: '+url
        text=self.gettextonly(sopa)
        words=self.separatewords(text)
        urlid=self.getentryid('urllist','url',url)
        for i in range(len(words)):
            word=words[i]
            if word in ignorewords: continue
            wordid=self.getentryid('wordlist','word',word)
            self.con.execute("insert into wordlocation(urlid,wordid,location) values (%d,%d,%d)" % (urlid,wordid,i))
                            
    # Extraindo o texto de uma pagina HTML sem as tags
    def gettextonly(self,soup):
        v=soup.string
        if v==None:   
            c=soup.contents
            resulttext=''
            for t in c:
                subtext=self.gettextonly(t)
                resulttext+=subtext+'\n'
            return resulttext
        else:
            return v.strip()

    # Separa as palavras por quaisquer caracteres que nao sejam espacos em branco
    def separatewords(self,text):
        splitter=re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s!='']
        
    def isindexed(self,url):
        u=self.con.execute("select rowid from urllist where url='%s'" %url).fetchone()
        if u!=None:
            # Verifica se a url ja foi visitada e indexada
            v=self.con.execute('select * from wordlocation where urlid=%d' %u[0]).fetchone()
            if v!=None: return True # Devolve 'true' se a url ja tiver sido indexada
        return False
        
    # Acrescenta um link entre duas paginas
    def addlinkref(self,urlFrom,urlTo,linkText):
        words=self.separatewords(linkText)
        fromid=self.getentryid('urllist','url',urlFrom)
        toid=self.getentryid('urllist','url',urlTo)
        if fromid==toid: return
        cur=self.con.execute("insert into link(fromid,toid) values (%d,%d)" % (fromid,toid))
        linkid=cur.lastrowid
        for word in words:
            if word in ignorewords: continue
            wordid=self.getentryid('wordlist','word',word)
            self.con.execute("insert into linkwords(linkid,wordid) values (%d,%d)" % (linkid,wordid))
    
    # Comeca com uma lista de paginas, faz uma busca em amplitude (breadth first)
    # ate uma profundidade determinada, indexando as paginas no caminho
    def crawl(self,pages,depth=1):
        print 'URL(s) da(s) pagina(s) semente: '        
        for p in pages: print p
        print
        print 'Indexando ate %s nivel(is) a partir da(s) pagina(s) semente'%depth
        for i in range(depth+1):
            newpages={}
            for page in pages:
                try:
                    c=urllib2.urlopen(page)
                except:
                    print "Nao foi possivel acessar: %s" %page
                    continue
                try:
                    p = c.read()
                    soup=BeautifulSoup(p)
                    self.addtoindex(page,soup) #Funcao addtoindex
                    links=soup('a')
                    for link in links:
                        if ('href' in dict(link.attrs)):
                            url=urljoin(page,link['href'])
                            if url.find("'")!=-1: continue
                            url=url.split('#')[0]  #Remove o que vier depois da url base
                            if url[0:4]=='http' and not self.isindexed(url):
                                newpages[url]=1
                            linkText=self.gettextonly(link)
                            self.addlinkref(page,url,linkText) #Adiciona link
                    self.dbcommit()
                except: 
                    #print "Could not parse page %s" % page
                    raise
            self.dbcommit()
            pages=newpages

    def calculatepagerank(self,iterations=20):
        # Limpa as tabelas atuais de pagerank se existirem, senao as cria
        self.con.execute('drop table if exists pagerank')
        self.dbcommit()
        self.con.execute('create table pagerank(urlid primary key,score)')
        # Inicializa cada url com o pagerank de valor "1"
        for (urlid,) in self.con.execute('select rowid from urllist'):
            self.con.execute('insert into pagerank(urlid,score) values (%d,1.0)' % urlid)
        self.dbcommit()
        for i in range(iterations):
            print "Iteration %d" % (i)
            for (urlid,) in self.con.execute('select rowid from urllist'):
                pr=0.15
                # Itera sobre todas as paginas que possuem links para esta
                for (linker,) in self.con.execute('select distinct fromid from link where toid=%d' % urlid):
                    # Recupera o pagerank da pagina que possui link (conectada) a essa
                    linkingpr=self.con.execute('select score from pagerank where urlid=%d' %linker).fetchone()[0]
                    # Recupera o numero total de links da pagina que possui link (conectada)
                    linkingcount=self.con.execute('select count(*) from link where fromid=%d' %linker).fetchone()[0]
                    pr+=0.85*(linkingpr/linkingcount)
                self.con.execute('update pagerank set score=%f where urlid=%d' % (pr,urlid))
            self.dbcommit()

#Fim do bloco de funcoes de Crawling
#Inicio do bloco de funcoes de Searching (busca)

class searcher:
    def __init__(self,dbname):
        self.con=sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def getmatchrows(self,q):
        # Campos para construcao da query
        fieldlist='w0.urlid'
        tablelist=''  
        clauselist=''
        wordids=[]
        # Separa as palavras nos espacos
        words=q.split(' ')  
        tablenumber=0
        for word in words:
            # Extrai o id da palavra
            wordrow=self.con.execute(
            "select rowid from wordlist where word='%s'" % word).fetchone()
            if wordrow!=None:
                wordid=wordrow[0]
                wordids.append(wordid)
                if tablenumber>0:
                    tablelist+=','
                    clauselist+=' and '
                    clauselist+='w%d.urlid=w%d.urlid and ' % (tablenumber-1,tablenumber)
                fieldlist+=',w%d.location' % tablenumber
                tablelist+='wordlocation w%d' % tablenumber      
                clauselist+='w%d.wordid=%d' % (tablenumber,wordid)
                tablenumber+=1
        # Cria a consulta a partir das partes separadas
        fullquery='select %s from %s where %s' % (fieldlist,tablelist,clauselist)
        #print fullquery
        cur=self.con.execute(fullquery)
        rows=[row for row in cur]
        return rows,wordids

    def getscoredlist(self,rows,wordids):
        totalscores=dict([(row[0],0) for row in rows])
        # Aqui devem ficar as funcoes que determinam o score das paginas
        weights=[(1.0,self.frequencyscore(rows)),
                 (1.0,self.locationscore(rows)), 
                 (1.0,self.distancescore(rows)),
                 (1.0,self.inboundlinkscore(rows)),
                 #(1.0,self.linktextscore(rows,wordids)),
                 (1.0,self.pagerankscore(rows))]
        for (weight,scores) in weights:
            for url in totalscores:
                totalscores[url]+=weight*scores[url]
        return totalscores

    def geturlname(self,id):
        return self.con.execute(
        "select url from urllist where rowid=%d" % id).fetchone()[0]

    def query(self,q):
        rows,wordids=self.getmatchrows(q)
        scores=self.getscoredlist(rows,wordids)
        rankedscores=[(score,url) for (url,score) in scores.items()]
        rankedscores.sort()
        rankedscores.reverse()
        print
        print 'Resultados para busca por %s :'%q
        for (score,urlid) in rankedscores[0:10]: #apresenta os 10 primeiros resultados
            print '%f\t%s' % (score,self.geturlname(urlid))
        return wordids,[r[1] for r in rankedscores[0:10]]

#Funcoes para calculo de relevancia

    def normalizescores(self,scores,smallIsBetter=0):
        vsmall=0.00001 # Para evitar erros de divisao por zero
        if smallIsBetter:
            minscore=min(scores.values())
            return dict([(u,float(minscore)/max(vsmall,l)) for (u,l) in scores.items()])
        else:
            maxscore=max(scores.values())
            if maxscore==0: maxscore=vsmall
            return dict([(u,float(c)/maxscore) for (u,c) in scores.items()])

    def frequencyscore(self,rows):
        counts=dict([(row[0],0) for row in rows])
        for row in rows: counts[row[0]]+=1
        return self.normalizescores(counts)

    def locationscore(self,rows):
        locations=dict([(row[0],1000000) for row in rows])
        for row in rows:
            loc=sum(row[1:])
            if loc<locations[row[0]]: locations[row[0]]=loc
        return self.normalizescores(locations,smallIsBetter=1)

    def distancescore(self,rows):
        # Se houver apenas uma palavra, todos saem ganhando!
        if len(rows[0])<=2: return dict([(row[0],1.0) for row in rows])
        # Inicializa o dicionario com grandes valores
        mindistance=dict([(row[0],1000000) for row in rows])
        for row in rows:
            dist=sum([abs(row[i]-row[i-1]) for i in range(1,len(row))])
            if dist<mindistance[row[0]]: mindistance[row[0]]=dist
        return self.normalizescores(mindistance,smallIsBetter=1)

    def inboundlinkscore(self,rows):
        uniqueurls=dict([(row[0],1) for row in rows])
        inboundcount=dict([(u,self.con.execute('select count(*) from link where toid=%d' % u).fetchone()[0]) for u in uniqueurls])   
        return self.normalizescores(inboundcount)

    def linktextscore(self,rows,wordids):
        linkscores=dict([(row[0],0) for row in rows])
        for wordid in wordids:
            cur=self.con.execute('select link.fromid,link.toid from linkwords,link where wordid=%d and linkwords.linkid=link.rowid' % wordid)
            for (fromid,toid) in cur:
                if toid in linkscores:
                    pr=self.con.execute('select score from pagerank where urlid=%d' % fromid).fetchone()[0]
                    linkscores[toid]+=pr
        maxscore=max(linkscores.values())
        normalizedscores=dict([(u,float(l)/maxscore) for (u,l) in linkscores.items()])
        return normalizedscores

    def pagerankscore(self,rows):
        pageranks=dict([(row[0],self.con.execute('select score from pagerank where urlid=%d' % row[0]).fetchone()[0]) for row in rows])
        maxrank=max(pageranks.values())
        normalizedscores=dict([(u,float(l)/maxrank) for (u,l) in pageranks.items()])
        return normalizedscores


if __name__ == '__main__':
    '''Defining seed pages'''
    seed = ['http://kiwitobes.com/wiki/Categorical_list_of_programming_languages.html']
    #seed = ['http://www.nytimes.com/']
    #seed = ['http://emap.fgv.br/']

    '''Instantiating the crawler'''
    c = crawler(db)
    c.createindextables() #Needed only in the first time
    c.crawl(sementes,1) #Define the depth level to crawl
    c.calculatepagerank(20) #number of iterations to pagerank
    
    '''Instantiating the searcher'''
    e = searcher(db)
    e.query('python')
