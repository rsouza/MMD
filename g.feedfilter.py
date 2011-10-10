""" 
Mestrado em Modelagem Matematica da Informacao
Disciplina de Modelagem e Mineracao de Dados
Professor: Renato Rocha Souza
Topico: Filtragem baseada em caracteristicas
"""

import feedparser
import re

# Recebe uma url de um feed rss e classifica as entradas
def read(feed,classifier):
    # Recebe as entradas do feed e itera em cada uma
    f=feedparser.parse(feed)
    for entry in f['entries']:
        print
        print '-----'
        # Exibe o conteúdo de uma entrada do feed
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
        cl=raw_input('Enter category: ')
        classifier.train(entry,cl)

def entryfeatures(entry):
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