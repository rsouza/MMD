#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Mestrado em Modelagem Matematica da Informacao
Master Program - Mathematical Modeling of Information

Disciplina: Modelagem e Mineracao de Dados
Course: Data Mining and Modeling

Professor: Renato Rocha Souza
Topic: Building Decision Trees (class #6)

Information on the Python Packages used:
http://www.pythonware.com/library/pil/handbook/index.htm
'''

from PIL import Image,ImageDraw
from math import log

'''Specifying the path to the files'''

datapath = "/home/rsouza/Documentos/Git/MMD/datasets/"
outputs = "/home/rsouza/Documentos/outputs/"

dataset1 = "ch06_bankPEP.txt"
dataset2 = "ch06_bankPEP_discrete"
dataset3 = "ch06_buldings.txt"
ftree1 = "arvore1.jpg"
ftree2 = "arvore2.jpg"
ftree3 = "arvore3.jpg"
ftree4 = "arvore4.jpg"

my_data1 = (datapath+dataset1)
my_data2 = (datapath+dataset2)
my_data3 = (datapath+dataset2)
figtree1 = (outputs+ftree1)
figtree2 = (outputs+ftree2)
figtree3 = (outputs+ftree3)
figtree4 = (outputs+ftree4)

''' Reads the dataset, separing Title and Data '''
def readfile(dataset):
    lines = [line for line in file(dataset)]
    categories = lines[0].strip().split(',')
    data = [line.strip().split(',') for line in lines[1:]]
    for i in range(len(data)):
        data[i][0]=int(float(data[i][0]))
        data[i][3]=int(float(data[i][3]))
        data[i][5]=int(float(data[i][5]))
    return categories, data

''' Class to store the data structure of the decision tree '''
class decisionnode:
    def __init__(self,col=-1,value=None,results=None,tb=None,fb=None):
        self.col=col #The chriterion to be tested
        self.value=value #The value that means True
        self.results=results #Dictionary with the node value, null if it is an endpoint
        self.tb=tb #next node in case of 'True'
        self.fb=fb #next node in case of 'False'

''' Divides an specific collumn in two sets, in which the first meets
    the chriteria and the second do not '''
def divideset(rows,column,value):
    split_function=None
    if isinstance(value,int) or isinstance(value,float):
        #If the value is numeric, divides the bigger or equal
        split_function=lambda row:row[column]>=value 
    else:
        #If it is categorical, divides the equals
        split_function=lambda row:row[column]==value
    # Divides the lines in two sets and return them
    set1=[row for row in rows if split_function(row)]
    set2=[row for row in rows if not split_function(row)]
    return (set1,set2)

''' Count the unique attributes from a collumn, returns a dictionary with counts'''
def uniquecounts(rows):
    results={}
    for row in rows:
        #Chooses the collumn to be tested for a value 
        r=row[len(row)-1] #In this dataset, it is the last one.
        if r not in results: 
            results[r]=1
        else:
            results[r]+=1
    return results

"""Funcoes para escolha do melhor seccionamento dos dados"""

""" Gini Impurity - Prob. de que um elemento aleatoriamente
    posicionado esteja na categoria errada  - quanto menor, melhor"""
def giniimpurity(rows):
    total=len(rows)
    counts=uniquecounts(rows)
    imp=0
    for k1 in counts:
        p1=float(counts[k1])/total
        for k2 in counts:
            if k1==k2: continue
            p2=float(counts[k2])/total
            imp+=p1*p2
    return imp

""" Entropia - a soma de p(x)log(p(x)) sobre todos os
    resultados possiveis - quanto menor, melhor"""
def entropy(rows):
    log2=lambda x:log(x)/log(2)  
    results=uniquecounts(rows)
    ent=0.0
    for r in results.keys():
        p=float(results[r])/len(rows)
        ent=ent-p*log2(p)
    return ent

""" Para datasets em que os resultados a serem preditos sao 
    numericos, a funcao variancia pode ser uma boa alternativa"""
def variance(rows):
    if len(rows)==0: return 0
    data=[float(row[len(row)-1]) for row in rows]
    mean=sum(data)/len(data)
    variance=sum([(d-mean)**2 for d in data])/len(data)
    return variance

"""Funcao primcipal que constroi a arvore, escolhendo o 
   melhor criterio para gerar uma divisao do conjunto de observacoes"""
def buildtree(rows,scoref=entropy):
    if len(rows)==0: return decisionnode()
    current_score=scoref(rows)
    # Variaveis que vao guardar o melhor criterio
    best_gain=0.0
    best_criteria=None
    best_sets=None
    column_count=len(rows[0])-1 #a ultima coluna fica de fora - de predicao
    for col in range(0,column_count): #itera sobre todas as colunas
        # Gera a lista dos diferentes valores na coluna
        column_values={}
        for row in rows:
            column_values[row[col]]=1 
        # Divide as linhas segundo cada um dos valores e calcula o ganho
        for value in column_values.keys():
            (set1,set2)=divideset(rows,col,value)
            # calculo do (possivel) ganho de informacao
            p=float(len(set1))/len(rows) #normaliza pelo numero de linhas
            gain=current_score-p*scoref(set1)-(1-p)*scoref(set2)
            if gain>best_gain and len(set1)>0 and len(set2)>0:
                best_gain=gain
                best_criteria=(col,value)
                best_sets=(set1,set2)
    # Cria os subramos da arvore   
    if best_gain>0:
        trueBranch=buildtree(best_sets[0])
        falseBranch=buildtree(best_sets[1])
        return decisionnode(col=best_criteria[0],value=best_criteria[1],
                            tb=trueBranch,fb=falseBranch)
    else:
        return decisionnode(results=uniquecounts(rows))

"""A funcao prune corrige a arvore, juntando subramos que nao
promovem um ganho minimo de informacao - variavel mingain"""
def prune(tree,mingain):
    # A funcao eh aplicada recursivamente se nao forem nohs finais
    if tree.tb.results==None: prune(tree.tb,mingain)
    if tree.fb.results==None: prune(tree.fb,mingain)
    # Quando finalmente se encontrar um no final, verifica-se se podem ser consolidados
    if tree.tb.results!=None and tree.fb.results!=None:
        # junta os dois conjuntos de resultados para testar se havia um ganho minimo
        tb,fb=[],[]
        for v,c in tree.tb.results.items(): tb+=[[v]]*c #cada item eh multiplicado
        for v,c in tree.fb.results.items(): fb+=[[v]]*c #pelo numero de vezes que aparece
        # Testa a reducao na entropia - pode-se usar outra funcao tambem para teste
        # Delta eh a entropia do consolidado menos a media da enropia dos individuais
        delta=entropy(tb+fb)-((entropy(tb)+entropy(fb))/2)
        print "delta: ", delta
        if delta<mingain:
            # Se o ganho minimo nao se observa, junta os subramos, formando um unico noh
            tree.tb,tree.fb=None,None
            tree.results=uniquecounts(tb+fb)

"""Funcoes para a exibicao da arvore de decisoes"""

"""Display Simples,por linhas de caracteres"""
def printtree(tree,indent=''):
    # Is this a leaf node?
    if tree.results!=None:
        print str(tree.results)
    else:
        # Exibe os criterios
        """Modifiquei a linha seguinte para mostrar os nomes reais das categorias""" 
        #print str(tree.col)+':'+str(tree.value)+'? '
        print cat[tree.col]+':'+str(tree.value)+'? ' #cat eh o cabecalho do dataset
        # Exibe os subramos
        print indent+'T->',
        printtree(tree.tb,indent+'  ')
        print indent+'F->',
        printtree(tree.fb,indent+'  ')

"""Display em arquivo jpg"""
def getwidth(tree):
    if tree.tb==None and tree.fb==None: return 1
    return getwidth(tree.tb)+getwidth(tree.fb)

def getdepth(tree):
    if tree.tb==None and tree.fb==None: return 0
    return max(getdepth(tree.tb),getdepth(tree.fb))+1

def drawnode(draw,tree,x,y):
    if tree.results==None:
        # Get the width of each branch
        w1=getwidth(tree.fb)*100
        w2=getwidth(tree.tb)*100
        # Determine the total space required by this node
        left=x-(w1+w2)/2
        right=x+(w1+w2)/2
        # Draw the condition string
        """Modifiquei a linha seguinte para mostrar os nomes reais das categorias"""       
       #draw.text((x-20,y-10),str(tree.col)+':'+str(tree.value),(0,0,0))
        draw.text((x-20,y-10),cat[tree.col]+':'+str(tree.value),(0,0,0)) #cat eh o cabecalho do dataset
        # Draw links to the branches
        draw.line((x,y,left+w1/2,y+100),fill=(255,0,0))
        draw.line((x,y,right-w2/2,y+100),fill=(255,0,0))
        # Draw the branch nodes
        drawnode(draw,tree.fb,left+w1/2,y+100)
        drawnode(draw,tree.tb,right-w2/2,y+100)
    else:
        txt=' \n'.join(['%s:%d'%v for v in tree.results.items()])
        draw.text((x-20,y),txt,(0,0,0))

def drawtree(tree,jpeg='tree.jpg'):
    w=getwidth(tree)*100
    h=getdepth(tree)*100+120
    img=Image.new('RGB',(w,h),(255,255,255))
    draw=ImageDraw.Draw(img)
    drawnode(draw,tree,w/2,20)
    img.save(jpeg,'JPEG')
  
"""Funcoes para classificar novas observacoes a partir da arvore treinada"""

def classify(observation,tree):
    if tree.results!=None: # testa para ver se eh um noh final
        return tree.results # se for, devolve as observacoes deste noh
    else: #se nao, testa qual o ramo que contem a observacao, e segue recursivamente
        v=observation[tree.col] #recebe o valor a ser testado
        branch=None
        if isinstance(v,int) or isinstance(v,float): #se forem dados numericos
            if v>=tree.value: branch=tree.tb #testa se esta no ramo direito
            else: branch=tree.fb #ou no esquerdo
        else:
            if v==tree.value: branch=tree.tb #se forem dados categoricos
            else: branch=tree.fb
        return classify(observation,branch)

"""A segunda (mdclassify) lida melhor com valores faltantes """
def mdclassify(observation,tree):
    if tree.results!=None: # testa para ver se eh um noh final
        return tree.results # se for, devolve as observacoes deste noh
    else:
        v=observation[tree.col]
        if v==None: # se o valor nao for conhecido na observacao, seguem-se os dois ramos
            tr,fr=mdclassify(observation,tree.tb),mdclassify(observation,tree.fb)
            tcount=sum(tr.values())
            fcount=sum(fr.values())
            tw=float(tcount)/(tcount+fcount) #calcula as proporcoes de observacoes
            fw=float(fcount)/(tcount+fcount) #de cada ramo em relacao ao total
            result={}
            for k,v in tr.items(): result[k]=v*tw #gera a lista de observacoes
            for k,v in fr.items(): result[k]=v*fw #ponderada pela proporcao
            return result
        else:
            if isinstance(v,int) or isinstance(v,float):
                if v>=tree.value: branch=tree.tb
                else: branch=tree.fb
            else:
                if v==tree.value: branch=tree.tb
                else: branch=tree.fb
            return mdclassify(observation,branch)

if __name__ == '__main__':
    cat, dados = readfile(my_data1) #Separa cabecalhos e dados
    set1,set2 = divideset(dados,1,'MALE') #Um exemplo de separacao do dataset
    print "giniimpurity do total eh: ", giniimpurity(dados)
    print "giniimpurity dos que a condicao se aplica: ", giniimpurity(set1)
    print "giniimpurity dos que a condicao nao se aplica: ", giniimpurity(set2)
    #print "entropia do total eh: ", entropy(dados)
    #print "entropia dos que a condicao se aplica: ", entropy(set1)
    #print "entropia dos que a condicao nao se aplica: ", entropy(set2)
    
    treeG = buildtree(dados, giniimpurity) #Montando a arvore c/ giniimpurity
    #printtree(treeG)
    drawtree(treeG, figtree1)
    
    treeE = buildtree(dados, entropy) #Montando outra arvore c/ entropia
    #printtree(treeE)
    drawtree(treeE, figtree2)
    
    #prune(treeE,0.96) #aplicando a funcao de verificacao de ganho minimo
    #drawtree(treeE, figtree3)
    
    #Agora usamos as funcoes de predicao, com o ultimo valor desconhecido
    classify([40,'MALE','TOWN',30085.1,'YES',3,'YES','NO','YES','YES'], treeE)
    classify([40,'MALE','TOWN',30085.1,'YES',3,'YES','NO','YES','YES'], treeG)
    
    #mdclassify lida melhor com valores faltantes
    mdclassify(['','MALE','TOWN',30085.1,'YES',3,'YES','NO','YES','YES'], treeG)
    
    
    treeV = buildtree(dados, variance) #Montando a arvore c/ variancia
    #prune(treeV,0.96) #aplicando a funcao de verificacao de ganho min
    printtree(treeV)
    drawtree(treeV, figtree4)
    
    #Agora usamos as funcoes de predicao, com o ultimo valor desconhecido
    classify([2139,2,1995,1512.0,2.5,4,6], treeV)