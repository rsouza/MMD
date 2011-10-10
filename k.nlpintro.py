# -*- coding:utf-8 -*-
""" 
Mestrado em Modelagem Matematica da Informacao
Disciplina de Modelagem e Mineracao de Dados
Professor: Renato Rocha Souza
Topico: Introducao ao PLN e recursos do NLTK
"""
import locale
import nltk
from nltk import ingrams, FreqDist
from nltk.corpus import PlaintextCorpusReader
#from nltk.tokenize import sent_tokenize

#Partes  de codigo adaptado de http://nltk.googlecode.com/svn/trunk/doc/howto/portuguese_en.html

corpus_root = '/home/rsouza/Dropbox/Light/PLN/'
stopwords = nltk.corpus.stopwords.words('portuguese')
ignorelist = [',','.',';','?','!','-',':','(',')','',' ','"',"'",'/']
eliminatelist = stopwords + ignorelist

#sent_tokenizer=nltk.data.load('tokenizers/punkt/portuguese.pickle') #com problemas

def createcorpus(pathtofiles):
    '''Cria corpus com arquivos .txt de uma pasta'''
    corpus = PlaintextCorpusReader(pathtofiles, '.*\.txt', encoding='UTF-8')
    print 'Criado corpus com os arquivos:'
    print corpus.fileids()
    return corpus

def corpus2collection(corpus):
    '''Consolida os textos do corpus em uma colecao'''
    tcollection = nltk.TextCollection(corpus)
    return tcollection

def analisecorpus(corpus):
    for fileid in corpus.fileids():
        num_chars = len(corpus.raw(fileid))
        num_words = len(corpus.words(fileid))
        tam_vocab = len(set([w.lower() for w in corpus.words(fileid)]))
        num_sents = len(corpus.sents(fileid))
        print 'Texto: ', fileid
        print 'Tamanho medio das palavras: ', num_chars/float(num_words)
        print 'Num. Medio de palavras por sentenca: ', num_words/float(num_sents)
        print 'Diversidade Lexical: ', tam_vocab/float(num_words)
       
def analiselight():
    corpuslight = createcorpus(corpus_root)
    tcollectlight = corpus2collection(corpuslight)
    tcollectlight.plot(30)
    tcollectlight.count('Light')
    tcollectlight.concordance('light')
    tcollectlight.concordance('TOI')
    tcollectlight.similar('Light')
    tcollectlight.common_contexts(['light','TOI'])
    tcollectlight.dispersion_plot(['Light','LIGHT','TOI'])
    
    txtlight = corpuslight.raw()
    txtlight_txt1 = corpuslight.raw('cc.txt')
    
    TEXTlight1 = nltk.Text(corpuslight.words('cc.txt')) #todos os metodos de tcollection
    TEXTlight1.count('Light')
    TEXTlight1.plot(80)

    sentslight = nltk.sent_tokenize(corpuslight.raw())
    sentslight_txt1 = nltk.sent_tokenize(corpuslight.raw('cc.txt'))

    tokenslight = corpuslight.words()
    tokenslight_txt1 = corpuslight.words('cc.txt')
    tokenslight_clean = [str(w.lower()) for w in tokenslight if str(w.lower()) not in eliminatelist]
    tokenslight_clean2 = [w for w in tokenslight_clean if w.isalpha() and len(w)>1] #opcional
    sorted(set(tokenslight_clean2), reverse=True)
    chosenwords = set([word for word in tokenslight_clean2 if 'admin' in word])
    
    names = sorted(set([z for x,z in nltk.bigrams(tokenslight) if (z.istitle() or z.isupper()) and len(z)>2 and x.isalpha()]))
    #names = sorted(set([str(w) for w in tokenslight if w.istitle() and len(w)>2]))
    for name in names: print str(name)

    fdlight = FreqDist(tokenslight_clean2)
    fdlight.items()[0:5]
    fdlight.freq('toi') #frequencia relativa
    fdlight.plot(30)
    fdlight.plot(cumulative = 'True')
    print '10 palavras mais frequentes'
    print fdlight.keys()[:10]
    print '10 palavras menos frequentes'
    print fdlight.keys()[-10:]
    
    #bigramas = [bg for bg in ingrams(tokenslight_clean2,2)]
    bigramas = nltk.bigrams(tokenslight_clean2)    
    fdbigram = FreqDist(bigramas)
    fdbigram.plot(30)
 
    trigramcond = [bgc for bgc in ingrams(tokenslight_clean,3) if 'light' in bgc]
    fdtrigramc = FreqDist(trigramcond)
    fdtrigramc.plot(30)
    for ng,c in fdtrigramc.items(): print ' '.join(ng), c #melhorando a exibicao
    

def analisemachado():
    from nltk.corpus import machado
    analisecorpus(machado)
    print machado.fileids(),
    print "numero de textos disponiveis: ",len(machado.fileids())
    machado.raw('romance/marm05.txt')
    machado_words = machado.words('romance/marm05.txt')
    machado_ngs = [qg for qg in ingrams(machado_words,4) if 'olho' in qg]
    fd = FreqDist(machado_ngs)
    fd.items()
    for ng,c in fd.items(): print ' '.join(ng), c #melhorando a exibicao



if __name__=="__main__":
    print 'recarregando modulos...'

