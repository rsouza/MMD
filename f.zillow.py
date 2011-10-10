""" 
Mestrado em Modelagem Matematica da Informacao
Disciplina de Modelagem e Mineracao de Dados
Professor: Renato Rocha Souza
Topico: Arvores de Decisao
"""

import xml.dom.minidom
import urllib2

#Requisitar uma chave no endereco:
#http://www.zillow.com/howto/api/APIOverview.htm
#https://www.zillow.com/webservice/Registration.htm
zwskey="X1-ZWz1btd7kfwfez_9myga"

#Especificando o caminho para o arquivo
datapath = "/home/rsouza/Dropbox/Renato/Python/MMD/"
addlist = "addresslist.txt"
outfile = "serie.txt"
state = 'Cambridge-MA'
addresslist = (datapath+addlist)
traindata = (datapath+outfile)

def getaddressdata(address,city):
    escad=address.replace(' ','+')
    url='http://www.zillow.com/webservice/GetDeepSearchResults.htm?'
    url+='zws-id=%s&address=%s&citystatezip=%s' % (zwskey,escad,city)
    doc=xml.dom.minidom.parseString(urllib2.urlopen(url).read())
    code=doc.getElementsByTagName('code')[0].firstChild.data
    if code!='0': return None
    if 1:
        zipcode=doc.getElementsByTagName('zipcode')[0].firstChild.data
        use=doc.getElementsByTagName('useCode')[0].firstChild.data
        year=doc.getElementsByTagName('yearBuilt')[0].firstChild.data
        sqft=doc.getElementsByTagName('finishedSqFt')[0].firstChild.data
        bath=doc.getElementsByTagName('bathrooms')[0].firstChild.data
        bed=doc.getElementsByTagName('bedrooms')[0].firstChild.data
        rooms=doc.getElementsByTagName('totalRooms')[0].firstChild.data
        price=doc.getElementsByTagName('amount')[0].firstChild.data
    else:
        return None
    return (int(zipcode),use,int(year),float(sqft),float(bath),int(bed),int(rooms),float(price))

def getpricelist(enderecos):
    l1=[]
    for line in file(enderecos):
        try:
            data=getaddressdata(line.strip(),state)
            l1.append(data)
            print data
        except:
            print "Registro incompleto"
    return l1

def criadados(enderecos,output):
    dic = {'Condominium':0,'SingleFamily':1,'Duplex':2,'Triplex':3}    
    dados = getpricelist(enderecos)
    dados = [reg for reg in dados if reg != None]
    out = file(output,'w')
    out.write('zipcode,type,year,sqft,bath,beds,rooms,price')
    out.write('\n')
    for linha in dados:
        linha = [str(l) for l in linha]
        for i in range(len(linha)):
            if linha[i] in dic.keys():
                linha[i]=str(dic[linha[i]])
            out.write(linha[i])
            if i != (len(linha)-1): out.write(',')
        out.write('\n') #como mapear os dados em numeros
    out.close()
    return dados

#dados = getpricelist(addresslist)
d = criadados(addresslist, traindata)