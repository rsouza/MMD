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
dataset2 = "ch06_bankPEP_discrete.txt"
dataset3 = "ch06_buldings.txt"
file1 = "decision_tree1.jpg"
file2 = "decision_tree2.jpg"
file3 = "decision_tree3.jpg"
file4 = "decision_tree4.jpg"
file5 = "decision_tree5.jpg"

my_data1 = (datapath+dataset1)
my_data2 = (datapath+dataset2)
my_data3 = (datapath+dataset3)
figtree1 = (outputs+file1)
figtree2 = (outputs+file2)
figtree3 = (outputs+file3)
figtree4 = (outputs+file4)
figtree5 = (outputs+file5)

def extract_header(dataset):
    ''' Reads the dataset, separing Headers and Data '''
    lines = [line for line in file(dataset)]
    categories = lines[0].strip().split(',')
    data = [line.strip().split(',') for line in lines[1:]]
    return categories, data

def convert_numerical(data, column_list):
    ''' Reads the data and converts specific textual columns to integers'''
    for i in range(len(data)):
        for column in column_list:
            data[i][column]=int(float(data[i][column]))
    return data

class decisionnode:
    ''' Class to store the data structure of the decision tree '''
    def __init__(self,col=-1,value=None,results=None,tb=None,fb=None):
        self.col=col #The chriterion to be tested
        self.value=value #The value that means True
        self.results=results #Dictionary with the node value, null if it is an endpoint
        self.tb=tb #next node in case of 'True'
        self.fb=fb #next node in case of 'False'

def divideset(rows,column,value):
    ''' Divides an specific column in two sets, in which the first meets
    the chriteria but not the second '''
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

def uniquecounts(rows):
    ''' Count the unique attributes from a column, 
    returns a dictionary with counts'''
    results={}
    for row in rows:
        #Chooses the column to be tested for a value 
        r=row[len(row)-1] #In this dataset, it is the last one.
        if r not in results: 
            results[r]=1
        else:
            results[r]+=1
    return results

'''Block of functions to choose the best data splits'''

def giniimpurity(rows):
    ''' Gini Impurity - measures the probability that a random chosen element
    is positioned in the wrong category - the less, the best are the values'''
    total=len(rows)
    counts=uniquecounts(rows)
    imp=0
    for k1 in counts:
        p1=float(counts[k1])/total
        for k2 in counts:
            if k1==k2: 
                continue
            p2=float(counts[k2])/total
            imp+=p1*p2
    return imp

def entropy(rows):
    '''Entropy measures the sum of p(x)log(p(x)) over all
    possible results - the less, the best are the values'''
    log2=lambda x:log(x)/log(2)  
    results=uniquecounts(rows)
    ent=0.0
    for r in results.keys():
        p=float(results[r])/len(rows)
        ent=ent-p*log2(p)
    return ent

def variance(rows):
    '''Variance works best for datasets in which the results to
    be predicted are numeric - the less, the best are the values '''
    if len(rows)==0: return 0
    data=[float(row[len(row)-1]) for row in rows]
    mean=sum(data)/len(data)
    variance=sum([(d-mean)**2 for d in data])/len(data)
    return variance

def buildtree(rows,scoref=entropy):
    '''Builds the tree,choosing the best chriterion to
    generate a split in the dataset'''
    if len(rows)==0: return decisionnode()
    current_score=scoref(rows)
    best_gain=0.0
    best_criteria=None
    best_sets=None
    column_count=len(rows[0])-1 #Last column in the dataset is to be predicted
    for col in range(0,column_count):
        column_values={}
        for row in rows:
            column_values[row[col]]=1 
        # Calculate the information gain of each value split
        for value in column_values.keys():
            (set1,set2)=divideset(rows,col,value)
            p=float(len(set1))/len(rows) #Normalize by the number of lines
            gain=current_score-p*scoref(set1)-(1-p)*scoref(set2)
            if gain>best_gain and len(set1)>0 and len(set2)>0:
                best_gain=gain
                best_criteria=(col,value)
                best_sets=(set1,set2) 
    if best_gain>0:     # Create subtrees
        trueBranch=buildtree(best_sets[0])
        falseBranch=buildtree(best_sets[1])
        return decisionnode(col=best_criteria[0],value=best_criteria[1],
                            tb=trueBranch,fb=falseBranch)
    else:
        return decisionnode(results=uniquecounts(rows))

def prune(tree,mingain):
    '''Corrects (Prune) the tree, aggregating subtrees in which the gain is
    lower than a threshold - in which there is little information gain.
    Applied recursively for all non terminal nodes.'''
    if tree.tb.results==None: 
        prune(tree.tb,mingain) #Test if terminal nodes
    if tree.fb.results==None: 
        prune(tree.fb,mingain) 
    if tree.tb.results!=None and tree.fb.results!=None:
        tb,fb=[],[] #Aggregates both subtrees and tests for the minimum gain
        for v,c in tree.tb.results.items(): tb += [[v]]*c
        for v,c in tree.fb.results.items(): fb += [[v]]*c
        delta=entropy(tb+fb)-((entropy(tb)+entropy(fb))/2)
        print "delta: ", delta
        if delta < mingain:
            tree.tb,tree.fb=None,None
            tree.results=uniquecounts(tb+fb)

'''Block of functions to display decision trees'''

def printtree(tree,indent=''):
    '''Simple comand line display'''
    if tree.results!=None:      # Is this a leaf node?
        print str(tree.results)
    else:
        #print str(tree.col)+':'+str(tree.value)+'? '
        print cat[tree.col]+':'+str(tree.value)+'? ' #cat is the column header
        print indent+'T->',
        printtree(tree.tb,indent+'  ')
        print indent+'F->',
        printtree(tree.fb,indent+'  ')

def getwidth(tree):
    if tree.tb==None and tree.fb==None: return 1
    return getwidth(tree.tb)+getwidth(tree.fb)

def getdepth(tree):
    if tree.tb==None and tree.fb==None: return 0
    return max(getdepth(tree.tb),getdepth(tree.fb))+1

def drawnode(draw,tree,x,y):
    if tree.results==None:
        w1=getwidth(tree.fb)*100 # Get the width of each branch
        w2=getwidth(tree.tb)*100
        left=x-(w1+w2)/2 # Determine the total space required by this node
        right=x+(w1+w2)/2
        # Draw the condition string
        #draw.text((x-20,y-10),str(tree.col)+':'+str(tree.value),(0,0,0))
        draw.text((x-20,y-10),cat[tree.col]+':'+str(tree.value),(0,0,0))
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
    '''Uses getwidth, getdepth and drawnode to create jpg file'''
    w=getwidth(tree)*100
    h=getdepth(tree)*100+120
    img=Image.new('RGB',(w,h),(255,255,255))
    draw=ImageDraw.Draw(img)
    drawnode(draw,tree,w/2,20)
    img.save(jpeg,'JPEG')
  
'''Block of functions to classify new observations useing the trained tree'''

def classify(observation,tree):
    if tree.results!=None: # Is this a leaf node?
        return tree.results
    else: 
        v=observation[tree.col]
        branch=None
        if isinstance(v,int) or isinstance(v,float): #treats numerica data
            if v>=tree.value: 
                branch=tree.tb
            else: 
                branch=tree.fb
        else:
            if v==tree.value: branch=tree.tb #treats categorial data
            else: branch=tree.fb
        return classify(observation,branch)

def mdclassify(observation,tree):
    '''This modified version works well with missing values'''    
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
    ''' Reads the dataset, separing Headers and Data '''
    cat, dados = extract_header(my_data1)
    dados = convert_numerical(dados, [0,3,5])
    #We can also try out our discretized dataset...
    #cat, dados = extract_header(my_data2)
    #dados = convert_numerical(dados, [5])

    set1,set2 = divideset(dados,1,'MALE')
    giw = giniimpurity(dados)
    gi1 = giniimpurity(set1)
    gi2 = giniimpurity(set2)
    p=float(len(set1))/len(dados) #Normalize by the number of lines
    gain_gi = giw - ((p*gi1) + ((1-p)*gi2))
    print('\nEstimating which algorithm provides best gains...\n')
    print('giniimpurity of the whole: {}'.format(giw))
    print('giniimpurity of first (True) set: {}'.format(gi1))
    print('giniimpurity of second (False) set: {}'.format(gi2))
    print('\ninformation gain = {}\n\n'.format(gain_gi))
    enw = entropy(dados)
    en1 = entropy(set1)
    en2 = entropy(set2)
    gain_entropy = enw - ((p*en1) + ((1-p)*en2))
    print('entropy of the whole: {}'.format(enw))
    print('entropy of first (True) set: {}'.format(en1))
    print('entropy of second (False) set: {}'.format(en2))
    print('\ninformation gain = {}\n\n'.format(gain_entropy))

    '''Building the textual and graphic trees'''
    treeG = buildtree(dados, giniimpurity)
    treeE = buildtree(dados, entropy)

    #printtree(treeG)
    drawtree(treeG, figtree1)
    
    #printtree(treeE)
    drawtree(treeE, figtree2)
    
    '''Pruning the trees (asserting minimal gains)'''    
    prune(treeG,0.96)
    prune(treeE,0.96)

    #printtree(treeG)
    drawtree(treeG, figtree3)
    
    #printtree(treeE)
    drawtree(treeE, figtree4)

    '''Classifying new observations using our trees
    The input is a data row without the value to be predicted'''
    
    print(classify([40,'MALE','TOWN',30085.1,'YES',3,'YES','NO','YES','YES'], treeE))
    print(classify([40,'MALE','TOWN',30085.1,'YES',3,'YES','NO','YES','YES'], treeG))
    
    #mdclassify function deals well with missing values
    print(mdclassify(['','MALE','TOWN',30085.1,'YES',3,'YES','NO','YES','YES'], treeG))
    
    '''Using variance, that deals best with numerical values
    Using a new dataset'''
    cat, dados = extract_header(my_data3)
    treeV = buildtree(dados, variance)
    #printtree(treeV)
    prune(treeV,0.96)
    #printtree(treeV)
    drawtree(treeV, figtree5)
    '''Classifying new observations using our tree
    The input is a data row without the value to be predicted'''    
    print(classify([2139,2,1995,1512.0,2.5,4,6], treeV))