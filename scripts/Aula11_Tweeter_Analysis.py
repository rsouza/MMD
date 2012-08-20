#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Mestrado em Modelagem Matematica da Informacao
Master Program - Mathematical Modeling of Information

Disciplina: Modelagem e Mineracao de Dados
Course: Data Mining and Modeling

Professor: Renato Rocha Souza
Topic: Twitter Analysis (class #11)

Information on the Python Packages used:
http://code.google.com/p/python-twitter/
http://networkx.lanl.gov/
http://docs.python.org/library/re.html
http://nltk.org/
http://ubietylab.net/ubigraph/content/Docs/index.html
http://docs.python.org/library/xmlrpclib.html
http://docs.python.org/library/webbrowser.html
http://docs.python.org/library/codecs.html
http://matplotlib.sourceforge.net/
http://numpy.scipy.org/
http://docs.python.org/library/itertools.html
http://docs.python.org/library/sys.html
http://docs.python.org/library/json.html
http://docs.python.org/library/os
'''

from __future__ import division
import twitter
import nltk
import re
import networkx as nx
import sys
import os
import json
import webbrowser
import codecs
import xmlrpclib
import ubigraph
from itertools import cycle
import numpy as np
from matplotlib.pyplot import plot, show, title, legend, figure

'''Specifying the path to the files'''

templates = "/home/rsouza/Documentos/Git/MMD/templates/"
outputs = "/home/rsouza/Documentos/outputs/"

dotfile = "graph_retweet.dot"
protofile = "graph_retweet.html"
tweetsfile = "Tweets_dump.txt"
template_proto = 'template_protoviz.html'

pathdotfile = (outputs+dotfile)
pathprotofile = (outputs+protofile)
pathtweetsfile = (outputs+tweetsfile)
pathtemplate = (templates+template_proto)

ubiServer = "http://127.0.0.1:20738/RPC2"

stoplist_en = nltk.corpus.stopwords.words('english')
stoplist_pt = nltk.corpus.stopwords.words('portuguese')
ignorewords = stoplist_en + stoplist_pt + ['',' ','-','rt']

''' 
Twitter API Keys 
Please generate yours...

ck = consumer_key
cs = consumer_secret
atk = access_token_key
ats = access_token_secret

https://dev.twitter.com/docs/auth/oauth
https://dev.twitter.com/apps/new
'''
ck = ''
cs = ''
atk = ''
ats = ''

'''Functions to access, retrieve and process Twitter Information:'''

def search_for_term(termo):
    '''Search and return tweets on a subject (5 pages of 100 results each)
    Save results in a file defined in "pathtweetsfile" '''
    search_results = []
    tweets = []
    tweets_txt = []
    tweets_words = []
    names = []
    for page in range(1,6):
        search_results.append(api.GetSearch(term=termo, per_page=100, page=page))
    for i in range(len(search_results)):
        for j in range(len(search_results[i])):
            tweets.append(search_results[i][j])
    tweets_txt += [str(tweet.text).split(' ') for tweet in tweets]
    for i in range(len(tweets)):
        tweets_words += [word.lower().strip(':@&$!?') for word in tweets_txt[i]]
    for i in range(len(tweets)): 
        names += [word.strip(':@&$!?') for word in tweets_txt[i] if word.istitle() and len(word) > 2]
    out = file(pathtweetsfile,'w')
    for tweet in tweets_txt: 
        out.write('\n{}'.format(tweet))
    return tweets, tweets_txt, tweets_words, names

def get_rt_origins(tweet):
    ''' Regex adapted from 
    http://stackoverflow.com/questions/655903/python-regular-expression-for-retweets'''
    rt_patterns = re.compile(r"(RT|via)((?:\b\W*@\w+)+)", re.IGNORECASE)
    rt_origins = []
    try:
        rt_origins += [mention.strip() for mention in rt_patterns.findall(tweet)[0][1].split()]
    except IndexError, e:
        pass
    return [rto.strip("@") for rto in rt_origins]

def create_graph_retweets(tweets):
    g = nx.DiGraph()
    for tweet in tweets:
        rt_origins = get_rt_origins(tweet.text)
        if not rt_origins:
            continue
        for rt_origin in rt_origins:
            g.add_edge(rt_origin, tweet.user.screen_name, {'tweet_id': tweet.id})
    return g

def save_dotfile(g):
    try:
        nx.drawing.write_dot(g, pathdotfile)
        print >> sys.stderr, 'Graph exported for file: {}'.format(pathdotfile)
    except (ImportError, UnicodeEncodeError): 
        # Este bloco serve para usuarios de windows, que certamente terao problemas
        # com o metodo nx.drawing.write_dot. Tambem serve para os casos em que temos
        # problemas com o unicode
        dot = ['"{}" -> "{}" [tweet_id={}]'.format(n1, n2, g[n1][n2]['tweet_id'])
               for (n1, n2) in g.edges()]
        f = codecs.open(pathdotfile, 'w', encoding='utf-8')
        f.write('''strict digraph {{}}'''.format(';\n'.join(dot), ))
        f.close()
        print >> sys.stderr, 'Graph exported for file: {}'.format(pathdotfile)
        return f.name

def save_protovis_file(g):
    '''A visualization alternative is "protovis" javascript
    It uses the files "template_protoviz.html and "protovis-r3.2.js"
    '''
    nodes = g.nodes()
    indexed_nodes = {}
    idx = 0
    for n in nodes:
        indexed_nodes.update([(n, idx,)])
        idx += 1
    links = []
    for n1, n2 in g.edges():
        links.append({'source': indexed_nodes[n2],'target': indexed_nodes[n1]})
    json_data = json.dumps({"nodes" : [{"nodeName" : n} for n in nodes], "links" : links}, indent=4)
    html = open(pathtemplate).read().format(json_data,)
    f = open(pathprotofile, 'w')
    f.write(html)
    f.close()
    print >> sys.stderr, 'Graph exported for file: {}'.format(pathprotofile)
    return f.name

def showing_in_ubigraph(graph, vstyles=[],estyles=[]):
    """
    Dynamic visualization using Ubigraph. Server should be
    running in the URL "ubiServer"
    graph.edges is a list of tuples: (n1,n2,w)
    """
    U = ubigraph.Ubigraph(URL=ubiServer)
    U.clear()
    nodes = {}
    edges = set([])
    #maxw = float(max(np.array([i[2] for i in graph.edges()]))) #largest weight
    if not vstyles:
        vstyles = cycle([U.newVertexStyle(id=1,shape="sphere", color="#ff0000")])
    else:
        vstyles = cycle(vstyles)
    rt_style = U.newVertexStyle(id=2,shape="sphere", color="#00ff00")
    for e in graph.edges():
        if e[0] not in nodes:
            n1 = U.newVertex(style=vstyles.next(), label=str(e[0]))#.decode('latin-1'))
            nodes[e[0]] = n1
        else:
            n1 = nodes[e[0]]
        if e[1] not in nodes:
            n2 = U.newVertex(style=rt_style, label=str(e[1]))
            nodes[e[1]] = n2
        else:
            n2 = nodes[e[1]]
        #es = e[2]/maxw
        if (n1,n2) not in edges:
            #U.newEdge(n1,n2,spline=True,strength=es, width=2.0, showstrain=True)
            U.newEdge(n1,n2,spline=True, width=2.0, showstrain=True)
            edges.add((n1,n2))
            edges.add((n2,n1))

'''Block for Lexical Analysis'''

goodwords =  ['Abundant','Accomplished','Achieving','Active','Admirable','Adorable',
              'Adventurous','Admired','Affluent','Agreeable','Alert','Aligned','Alive',
              'Amazing','Appealing','Appreciate','Artistic','Astounding','Astute',
              'Attentive','Attractive','Auspicious','Authentic','Awake','Aware','Awesome',
              'Beaming','Beautiful','Better','Best','Blessed','Bliss','Bold','Bright','Brilliant',
              'Brisk','Buoyant','Calm','Capable','Centered','Certain','Charming',
              'Cheerful','Clear','Clever','Competent','Complete','Confident','Connected',
              'Conscious','Considerate','Convenient','Courageous','Creative','Daring',
              'Dazzling','Delicious','Delightful','Desirable','Determined','Diligent',
              'Discerning','Discover','Dynamic','Eager','Easy','Efficient','Effortless',
              'Elegant','Eloquent','Energetic','Endless','Enhancing','Engaging','Enormous'
              ,'Enterprising','Enthusiastic','Enticing','Excellent','Exceptional','Exciting'
              ,'Experienced','Exquisite','Fabulous','Fair','Far-Sighted','Fascinating',
              'Fine','Flattering','Flourishing','Fortunate','Free','Friendly','Fulfilled',
              'Fun','Generous','Genuine','Gifted','Glorious','Glowing','Good','Good-Looking',
              'Gorgeous','Graceful','Gracious','Grand','Great','Handsome','Happy','Hardy',
              'Harmonious','Healed','Healthy','Helpful','Honest','Humorous','Ideal',
              'Imaginative','Impressive','Industrious','Ingenious','Innovative','Inspired',
              'Intelligent','Interested','Interesting','Intuitive','Inventive','Invincible',
              'Inviting','Irresistible','Joyous','Judicious','Keen','Kind','Knowing','Leader',
              'Limitless','Lively','Loving','Lucky','Luminous','Magical','Magnificent',
              'Marvellous','Masterful','Mighty','Miraculous','Motivated','Natural','Neat',
              'Nice','Nurturing','Noble','Optimistic','Outstanding','Passionate','Peaceful',
              'Perfect','Persevering','Persistent','Playful','Pleasing','Plentiful','Positive',
              'Powerful','Precious','Prepared','Productive','Profound','Prompt','Prosperous',
              'Proud','Qualified','Quick','Radiant','Reasonable','Refined','Refreshing',
              'Relaxing','Reliable','Remarkable','Resolute','Resourceful','Respected',
              'Rewarding','Robust','Safe','Satisfied','Secure','Seductive','Self-Reliant',
              'Sensational','Sensible','Sensitive','Serene','Sharing','Skilful','Smart',
              'Smashing','Smooth','Sparkling','Spiritual','Splendid','Strong','Stunning',
              'Successful','Superb','Swift','Talented','Tenacious','Terrific','Thankful',
              'Thrilling','Thriving','Timely','Trusting','Truthful','Ultimate','Unique',
              'Valiant','Valuable','Versatile','Vibrant','Victorious','Vigorous','Vivacious',
              'Vivid','Warm','Wealthy','Well','Whole','Wise','Wonderful','Worthy','Young',
              'Youthful','Zeal','Zest']

badwords =   ['abandoned','abused','accused','addicted','afraid','aggravated',
              'aggressive','alone','angry','anguish','annoyed','anxious','apprehensive',
              'argumentative','artificial','ashamed','assaulted','at a loss','at risk',
              'atrocious','attacked','avoided','awful','awkward','bad','badgered','baffled',
              'banned','barren','beat','beaten down','belittled','berated','betrayed',
              'bitched at','bitter','bizzare','blacklisted','blackmailed','blamed','bleak',
              'blown away','blur','bored','boring','bossed-around','bothered','bothersome',
              'bounded','boxed-in','broken','bruised','brushed-off','bugged','bullied',
              'bummed','bummed out','burdened','burdensome','burned','burned-out',
              'caged in','careless','chaotic','chased','cheated','cheated on','chicken',
              'claustrophobic','clingy','closed','clueless','clumsy','coaxed',
              'codependent','coerced','cold','cold-hearted','combative','commanded',
              'compared','competitive','compulsive','conceited','concerned',
              'condescended to','confined','conflicted','confronted','confused',
              'conned','consumed','contemplative','contempt','contentious','controlled',
              'convicted','cornered','corralled','cowardly','crabby','cramped','cranky',
              'crap','crappy','crazy','creeped out','creepy','critical','criticized',
              'cross','crowded','cruddy','crummy','crushed','cut-down','cut-off','cynical',
              'damaged','damned','dangerous','dark','dazed','dead','deceived','deep',
              'defamed','defeated','defective','defenseless','defensive','defiant',
              'deficient','deflated','degraded','dehumanized','dejected','delicate',
              'deluded','demanding','demeaned','demented','demoralized','demotivated',
              'dependent','depleted','depraved','depressed','deprived','deserted',
              'deserving of pain/punishment','desolate','despair','despairing',
              'desperate','despicable','despised','destroyed','destructive',
              'detached','detest','detestable','detested','devalued','devastated',
              'deviant','devoid','diagnosed','dictated to','different','difficult',
              'directionless','dirty','disabled','disagreeable','disappointed',
              'disappointing','disapproved of','disbelieved','discardable','discarded',
              'disconnected','discontent','discouraged','discriminated','disdain',
              'disdainful','disempowered','disenchanted','disgraced','disgruntled',
              'disgust','disgusted','disheartened','dishonest','dishonorable',
              'disillusioned','dislike','disliked','dismal','dismayed','disorganized',
              'disoriented','disowned','displeased','disposable','disregarded',
              'disrespected','dissatisfied','distant','distracted','distraught',
              'distressed','disturbed','dizzy','dominated','doomed','double-crossed',
              'doubted','doubtful','down','down and out','down in the dumps',
              'downhearted','downtrodden','drained','dramatic','dread','dreadful',
              'dreary','dropped','drunk','dry','dumb','dumped','dumped on','duped',
              'edgy','egocentric','egotistic','egotistical','elusive','emancipated',
              'emasculated','embarrassed','emotional','emotionless','emotionally bankrupt',
              'empty','encumbered','endangered','enraged','enslaved','entangled','evaded',
              'evasive','evicted','excessive','excluded','exhausted','exploited','exposed',
              'fail','failful','fake','false','fear','fearful','fed up','flawed','forced',
              'forgetful','forgettable','forgotten','fragile','freaked out','frightened',
              'frigid','frustrated','furious','gloomy','glum','gothic','grey','grief','grim',
              'gross','grossed-out','grotesque','grouchy','grounded','grumpy','guilt-tripped',
              'guilty','harassed','hard','hard-hearted','harmed','hassled','hate','hateful',
              'hatred','haunted','heartbroken','heartless','heavy-hearted','helpless',
              'hesitant','hideous','hindered','hopeless','horrible','horrified','horror',
              'hostile','hot-tempered','humiliated','hung up','hung over','hurried','hurt',
              'hysterical','idiot','idiotic','ignorant','ignored','ill','ill-tempered',
              'imbalanced','imposed-upon','impotent','imprisoned','impulsive','in the dumps',
              'in the way','inactive','inadequate','incapable','incommunicative','incompetent',
              'incompatible','incomplete','incorrect','indecisive','indifferent',
              'indoctrinated','inebriated','ineffective','inefficient','inferior',
              'infuriated','inhibited','inhumane','injured','injusticed','insane',
              'insecure','insignificant','insincere','insufficient','insulted',
              'intense','interrogated','interrupted','intimidated','intoxicated',
              'invalidated','invisible','irrational','irritable','irritated',
              'isolated','jaded','jealous','jerked around','joyless','judged',
              'kept apart','kept away','kept in','kept out','kept quiet','labeled',
              'laughable','laughed at','lazy','leaned on','lectured to','left out',
              'let down','lied about','lied to','limited','little','lonely','lonesome',
              'longing','lost','lousy','loveless','low','mad','made fun of','man handled',
              'manipulated','masochistic','messed with','messed up','messy','miffed',
              'miserable','misled','mistaken','mistreated','mistrusted','misunderstood',
              'mixed-up','mocked','molested','moody','nagged','needy','negative',
              'nervous','neurotic','nonconforming','numb','nuts','nutty','objectified',
              'obligated','obsessed','obsessive','obstructed','odd','offended',
              'on display','opposed','oppressed','out of place','out of touch',
              'over-controlled','over-protected','overwhelmed','pain','panic','paranoid',
              'passive','pathetic','pessimistic','petrified','phony','picked on','pissed',
              'pissed off','plain','played with','pooped','poor','powerless','pre-judged',
              'preached to','preoccupied','predjudiced','pressured','prosecuted',
              'provoked','psychopathic','psychotic','pulled apart','pulled back',
              'punished','pushed','pushed away','put down','puzzled','quarrelsome',
              'queer','questioned','quiet','rage','raped','rattled','regret','rejected',
              'resented','resentful','responsible','retarded','revengeful','ridiculed',
              'ridiculous','robbed','rotten','sad','sadistic','sarcastic','scared',
              'scarred','screwed','screwed over','screwed up','self-centered','self-conscious',
              'self-destructive','self-hatred','selfish','sensitive','shouted at','shy',
              'singled-out','slow','small','smothered','snapped at','spiteful','stereotyped',
              'strange','stressed','stretched','stuck','stupid','submissive','suffering',
              'suffocated','suicidal','superficial','suppressed','suspicious','worse','worst'
              ,'bankrupcy','jobs','shit','socialism','#sob']
                  

def lexical_diversity(text):
    return len(text) / len(set(text))
    
def percentage(count, total):
    return 100 * count / total

def sentiment_analysis(texto, goodwords, badwords):
    '''
    Not a sophisticated one, but the main idea is present.
    Please read: http://alias-i.com/lingpipe/demos/tutorial/sentiment/read-me.html
    '''
    goodness = 0
    badness = 0    
    for word in listabom:
        goodness += percentage(texto.count(word.lower()), len(texto))
    for word in listamal:
        badness += percentage(texto.count(word.lower()), len(texto))
    print 'Grau de negatividade: {}'.format(badness)
    print 'Grau de positividade: {}'.format(goodness)
    return goodness, badness

    
if __name__ == '__main__':
    #api = twitter.Api() # Accessing with no authentication
    api = twitter.Api(consumer_key = ck, consumer_secret = cs, 
                      access_token_key = atk, access_token_secret = ats)

    '''Recent public messages'''
    msgpublicas = api.GetPublicTimeline() 
    print([s.user.name for s in msgpublicas])

    '''Recent messages from an user'''
    msguser = api.GetUserTimeline('rrsouza')
    print([s.text for s in msguser])

    '''Searching for a term in tweets'''
    search = api.GetSearch('Petrobras')
    print([s.text for s in search])
    
    '''After authentication, more options are available'''
    userfollow = api.GetFriends()
    print([u.name for u in userfollow])
    
    userfollowers = api.GetFollowers()
    print([u.name for u in userfollowers])
    
    userfriendstimeline = api.GetFriendsTimeline()
    print([u.text for u in userfriendstimeline])

    '''Using our customized function that retrieves 5 x 100 tweets'''
    tweets, tweets_txt, tweets_words, names = search_for_term('London')          
    
    print('Word count: {}'.format(len(tweets_words)))
    print('Repertoire: {}'.format(len(set(tweets_words))))
    print('Lexical diversity: {}'.format(lexical_diversity(tweets_words)))
    
    freq_dist = nltk.FreqDist(tweets_words)
    freq_dist.plot(40)
    #freq_dist.plot(40, cumulative = True)    
    
    print('10 most frequent words')
    print(freq_dist.keys()[:10])
    print('10 less frequent words')
    print(freq_dist.keys()[-10:])
    print('Sorted list of words')
    print(sorted(set(tweets_words)))

    '''Same as before, without stopwords. See variable "ignorewords"'''    
    new_tweets_words = [word for word in tweets_words if word not in ignorewords]
    freq_new = nltk.FreqDist(new_tweets_words)    
    freq_new.plot()
    freq_new.plot(40)
    freq_new.plot(40, cumulative = True)
    
    print('10 most frequent words')
    print(freq_new.keys()[:10])
    print('10 less frequent words')
    print(freq_new.keys()[-10:])
    print('Sorted list of words')
    print(sorted(set(new_tweets_words)))    
    
    '''Counting specific words'''
    new_tweets_words.count('bad')
    new_tweets_words.count('good')
    freq_new['good'] #same as before
    freq_new.freq('good') #relative to the others
    
    '''Eliminating small word'''
    bigger_tweets_words = [word for word in new_tweets_words if len(word) > 2]
    
    '''Words with specific sizes'''  
    mediumsized_tweets_words = [word for word in new_tweets_words if len(word) > 2 and len(word) < 9]

    '''Citation Analysis'''
    citacoes = [word for word in tweets_words if word.startswith('@')]
    freq_citacoes = nltk.FreqDist(citacoes)
    freq_citacoes.items()
    freq_citacoes.plot()

    '''Hashtag Analysis'''
    hashtags = [word for word in tweets_words if word.startswith('#')]
    freq_hashtags = nltk.FreqDist(hashtags)
    freq_hashtags.items()
    freq_hashtags.plot()

    '''Analysis of Frequent words
    Can be used with any of the previous lists'''
    frequent_words = [word.lower() for word in new_tweets_words if tweets_words.count(word) > 5]
    freq_dist2 = nltk.FreqDist(frequent_words)
    freq_dist2.plot()

    '''Words Sizes'''
    freqtamwords = nltk.FreqDist([len(w) for w in new_tweets_words])
    freqtamwords.items()
    freqtamwords.plot()

    '''Bigrams'''
    bigramas_tweets = nltk.bigrams(new_tweets_words)
    freqbig = nltk.FreqDist(bigramas_tweets)
    freqbig.plot(20)

    '''Names (capitalized words)'''
    freq_names = nltk.FreqDist(names)
    freq_names.plot(20)

    '''Sentiment Analysis'''
    sentiment_analysis(tweets_words, lista_positiva, lista_negativa)
    
    '''
    Graphs
    Obs: To generate a png graph from the dotfile, type in the Unix Prompt: 
    'circo -Tpng -Gcharset=latin1 -Ograph_retweet graph_retweet.dot'
    '''
    g_rt = create_graph_retweets(tweets)
    #print(g_rt.number_of_nodes())
    #print(g_rt.number_of_edges())
    #print(nx.degree(g_rt))
    dic = nx.degree(g_rt)
    #print(sorted(dic.values()))
    plot(sorted(dic.values()))
    save_dotfile(g_rt)
    save_protovis_file(g_rt)
    showing_in_ubigraph(g_rt)


