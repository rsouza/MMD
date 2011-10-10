""" 
Mestrado em Modelagem Matematica da Informacao
Disciplina de Modelagem e Mineracao de Dados
Professor: Renato Rocha Souza
Topico: Arvores de Decisao
"""

from PIL import Image,ImageDraw #http://www.pythonware.com/library/pil/handbook/index.htm
from math import log

#Especificando o caminho para o arquivo
datapath = "/home/rsouza/Dropbox/Renato/Python/MMD/"
dataset1 = "bank.txt"
dataset2 = "serie.txt"
ftree1 = "arvore1.jpg"
ftree2 = "arvore2.jpg"
ftree3 = "arvore3.jpg"
ftree4 = "arvore4.jpg"
my_data = (datapath+dataset1)
my_data2 = (datapath+dataset2)
figtree1 = (datapath+ftree1)
figtree2 = (datapath+ftree2)
figtree3 = (datapath+ftree3)
figtree4 = (datapath+ftree4)

""" Le o dataset, separando titulos e dados"""
def readfile(filename):
    lines = [line for line in file(filename)]
    #separa a primeira linha pelas virgulas, retira chars estranhos
    categories = lines[0].strip().split(',')
    #idem para as subsequentes    
    data = [line.strip().split(',') for line in lines[1:]]
    for i in range(len(data)):
        for j in range(8):
            data[i][j]=float(data[i][j])
    return categories,data

""" Classe que vai guardar a estrutura de dados da arvore de decisao"""
class decisionnode:
    def __init__(self,col=-1,value=None,results=None,tb=None,fb=None):
        self.col=col #a coluna com o criterio a ser testado
        self.value=value #valor que corresponde a 'true'
        self.results=results #dicionario com os resultados para o noh, nulo se nao for um endpoint
        self.tb=tb #proximo noh, caso 'true'
        self.fb=fb #proximo noh, caso 'false'

""" Funcao para dividir uma coluna especifica em dois conjuntos,
    em que o primeiro atende um criterio e o segundo nao"""
def divideset(rows,column,value):
    split_function=None
    if isinstance(value,int) or isinstance(value,float):
        #Se o valor eh numerico, separa os maiores ou iguais
        split_function=lambda row:row[column]>=value 
    else:
        #Se o valor eh categorico, separa os iguais
        split_function=lambda row:row[column]==value
    # Divide as linhas em dois conjuntos e os retorna
    set1=[row for row in rows if split_function(row)]
    set2=[row for row in rows if not split_function(row)]
    return (set1,set2)

""" Funcao para contar os atributos unicos de uma coluna
    Devolve um dicionario com os valores e suas contagens"""
def uniquecounts(rows):
    results={}
    for row in rows:
        #Escolhe a coluna com o valor a ser testado 
        r=row[len(row)-1] #Neste dataset, eh a ultima coluna
        if r not in results: results[r]=1
        else: results[r]+=1
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

"""Programa Principal"""

cat,dados = readfile(my_data2) #Separa cabecalhos e dados
treeV = buildtree(dados, variance) #Montando a arvore c/ variancia
#prune(treeV,0.96) #aplicando a funcao de verificacao de ganho min
printtree(treeV)
drawtree(treeV, figtree4)

#Agora usamos as funcoes de predicao, com o ultimo valor desconhecido
classify([2139,2,1995,1512.0,2.5,4,6], treeV)