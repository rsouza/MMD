#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Mestrado em Modelagem Matematica da Informacao
Master Program - Mathematical Modeling of Information

Disciplina: Modelagem e Mineracao de Dados
Course: Data Mining and Modeling

Professor: Renato Rocha Souza
Topic: Facebook, Visualization and NLP Analysis (class #12)

Code adapted from:
    facebook__login.py,
    facebook__graph_query.py,
    facebook__fql_query.py,
    facebook__get_friends_rgraph.py,
    facebook__sunburst.py,
    facebook__popularity_spreadsheet.py
    facebook__filter_rgraph_output_by_group.py,
    facebook__tag_cloud.py

An endpoint example is implemented in http://miningthesocialweb.appspot.com/

Information on the Python Packages used:
http://docs.python.org/library/os
http://docs.python.org/library/sys.html
http://docs.python.org/library/webbrowser.html
http://docs.python.org/library/urllib.html
http://docs.python.org/library/urllib2.html
http://docs.python.org/library/json.html
https://github.com/facebook/python-sdk
http://nltk.org/
http://docs.python.org/library/shutil.html
http://docs.python.org/library/operator.html
http://docs.python.org/library/copy.html
http://docs.python.org/library/cgi.html
'''

import os
import sys
import webbrowser
import urllib
from urllib import urlencode
import urllib2
import json
import facebook
import nltk
import shutil
import operator
from copy import deepcopy
from cgi import escape

''' 
Please generate your Facebook API Keys
http://www.facebook.com/developers

Application must be autorized in:
http://developers.facebook.com/docs/authentication/
'''

AppID = ''
AppSecret = ''
ACCESS_TOKEN = ''
SiteURL = 'http://miningthesocialweb.appspot.com/static/facebook_oauth_helper.html'
LIMIT = 100

'''Specifying the path to the files'''

templates = "/home/rsouza/Documentos/Git/MMD/templates/"
outputs = "/home/rsouza/Documentos/outputs/"

#current = os.getcwd()
#if not os.path.isdir('outputs'): os.mkdir('outputs')
#outputs = os.path.join(current, 'outputs')
#f = open(os.path.join(os.getcwd(), 'out', 'jit', 'sunburst', OUT), 'w')
#if not os.path.isdir('out'): os.mkdir('out')
#filename = os.path.join('outputs', 'facebook.spreadsheet.csv')

tagcloud_template = 'template_tagcloud.html'
sunburst_template = 'template_sunburst.html'
rgraph_template = 'template_rgraph.html'

graphhtml = 'fb_amigos.html'
graphhtmlgroup = 'fb_amigos_group.html'
graphjson = 'fb_amigos.json'
graphsun = 'fb_amigos_sun.html'
graphcloud = 'fb_tag_cloud.html'
csvfile = 'fb_amigos.csv'

tagcloudtemplate = (templates+tagcloud_template)
sunbursttemplate = (templates+sunburst_template)
rgraphtemplate = (templates+rgraph_template)

rgraphfile = (outputs+graphhtml)
rgraphfile2 = (outputs+graphhtmlgroup)
dumpjson = (outputs+graphjson)
sungraphfile = (outputs+graphsun)
graphcloudfile = (outputs+graphcloud)
spreadsheet = (outputs+csvfile)

def login():
    '''
    You could customize which extended permissions are being requested on the login 
    page or by editing the list below. By default, all the ones that make sense for  
    read access as described on http://developers.facebook.com/docs/authentication/ 
    are included. (And yes, it would be probably be ridiculous to request this much 
    access if you wanted to launch a successful production application.)
    '''
    CLIENT_ID = AppID
    REDIRECT_URI = SiteURL
    EXTENDED_PERMS = [
            'user_about_me',
            'friends_about_me',
            'user_activities',
            'friends_activities',
            'user_birthday',
            'friends_birthday',
            'user_education_history',
            'friends_education_history',
            'user_events',
            'friends_events',
            'user_groups',
            'friends_groups',
            'user_hometown',
            'friends_hometown',
            'user_interests',
            'friends_interests',
            'user_likes',
            'friends_likes',
            'user_location',
            'friends_location',
            'user_notes',
            'friends_notes',
            'user_online_presence',
            'friends_online_presence',
            'user_photo_video_tags',
            'friends_photo_video_tags',
            'user_photos',
            'friends_photos',
            'user_relationships',
            'friends_relationships',
            'user_religion_politics',
            'friends_religion_politics',
            'user_status',
            'friends_status',
            'user_videos',
            'friends_videos',
            'user_website',
            'friends_website',
            'user_work_history',
            'friends_work_history',
            'email',
            'read_friendlists',
            'read_requests',
            'read_stream',
            'user_checkins',
            'friends_checkins',
            ]

    args = dict(client_id=CLIENT_ID, redirect_uri=REDIRECT_URI,
                scope=','.join(EXTENDED_PERMS), type='user_agent', display='popup')
    webbrowser.open('https://www.facebook.com/dialog/oauth?'+ urllib.urlencode(args))
    access_token = raw_input('Enter your access_token: ')
    os.path.walk(outputs)
    if not os.path.isdir('out'): os.mkdir('out')
    filename = os.path.join('out', 'facebook.access_token')
    f = open(filename, 'w')
    f.write(access_token)
    f.close()
    print >> sys.stderr, "Access token stored to local file: 'out/facebook.access_token'"
    return access_token

def find_groups(query):
    # Query to the Facebook GRAPH API 
    # http://developers.facebook.com/tools/explorer/
    # Search groups based on a 'query', limited by LIMIT
    group_ids = []
    i = 0
    while True:
        results = gapi.request('search', {'q': query,'type': 'group','limit': LIMIT,
                               'offset': LIMIT * i,})
        if not results['data']: 
            break
        ids = [group['id'] for group in results['data'] if group['name'
               ].lower().find('programming') > -1]
        # once groups stop containing the term we are looking for in their name, bail out
        if len(ids) == 0:
            break
        group_ids += ids
        i += 1
    if not group_ids:
        print 'No results'
        sys.exit()
    # Get details for the groups
    groups = gapi.get_objects(group_ids, metadata=1)
    # Count the number of members in each group. The FQL API documentation at
    # http://developers.facebook.com/docs/reference/fql/group_member hints that for
    # groups with more than 500 members, we'll only get back a random subset of up
    # to 500 members.
    for g in groups:
        group = groups[g]
        conn = urllib2.urlopen(group['metadata']['connections']['members'])
        try: 
            members = json.loads(conn.read())['data']
        finally: 
            conn.close()
        print group['name'], len(members)
        

class FQL(object):
    #Classe for complex queries using FQL
    #http://developers.facebook.com/docs/reference/fql/
    # A most powerful alternative to GRAPH API
    ENDPOINT = 'https://api.facebook.com/method/'

    def __init__(self, access_token=None):
        self.access_token = access_token

    def _fetch(cls, url, params=None):
        conn = urllib2.urlopen(url, data=urlencode(params))
        try:
            return json.loads(conn.read())
        finally:
            conn.close()

    def query(self, q):
        if q.strip().startswith('{'):
            return self.multiquery(q)
        else:
            params = dict(query=q, access_token=self.access_token, format='json')
            url = self.ENDPOINT + 'fql.query'
            return self._fetch(url, params=params)

    def multiquery(self, q):
        params = dict(queries=q, access_token=self.access_token, format='json')
        url = self.ENDPOINT + 'fql.multiquery'
        return self._fetch(url, params=params)


def fql_queries(fqlquery):
    fql = FQL(access_token=ACCESS_TOKEN)
    result = fql.query(fqlquery)
    print json.dumps(result, indent=4)
    return result

def graph_friends():
    '''
    Now get friendships amongst your friends. note that this api appears to return 
    arbitrarily truncated results if you pass in more than a couple hundred friends 
    into each part of the query, so we perform (num friends)/N queries and aggregate 
    the results to try and get complete results
    Warning: this can result in a several API calls and a lot of data returned that 
    you'll have to process
    Get details about your friends, such as first and last name and create an accessible map
    note that not every id will necessarily information so be prepared to handle those cases 
    later
    '''
    fql = FQL(access_token=ACCESS_TOKEN)
    q = "select target_id from connection where source_id = me() and target_type ='user'"
    my_friends = [str(t['target_id']) for t in fql.query(q)]
    mutual_friendships = []
    N = 50
    for i in range(len(my_friends) / N + 1):
        q = 'select uid1, uid2 from friend where uid1 in (%s) and uid2 in (%s)' \
        %(','.join(my_friends), ','.join(my_friends[i * N:(i + 1) * N]))
        mutual_friendships += fql.query(q)   
    q = 'select uid, first_name, last_name, sex from user where uid in (%s)' \
    % (','.join(my_friends), )
    results = fql.query(q)
    names = dict([(unicode(u['uid']), u['first_name'] + ' ' + u['last_name'][0] + '.'
             ) for u in results])
    sexes = dict([(unicode(u['uid']), u['sex']) for u in results])
    # consolidate a map of connection info about your friends.
    friendships = {}
    for f in mutual_friendships:
        (uid1, uid2) = (unicode(f['uid1']), unicode(f['uid2']))
        try: name1 = names[uid1]
        except KeyError, e:
            name1 = 'Unknown'
        try: name2 = names[uid2]
        except KeyError, e:
            name2 = 'Unknown'
        if friendships.has_key(uid1):
            if uid2 not in friendships[uid1]['friends']:
                friendships[uid1]['friends'].append(uid2)
        else:
            friendships[uid1] = {'name': name1, 'sex': sexes.get(uid1, ''),
                                 'friends': [uid2]}
        if friendships.has_key(uid2):
            if uid1 not in friendships[uid2]['friends']:
                friendships[uid2]['friends'].append(uid1)
        else:
            friendships[uid2] = {'name': name2, 'sex': sexes.get(uid2, ''),
                                 'friends': [uid1]}
    return friendships, names, sexes, mutual_friendships
    
def generate_rgraph_friends(friendships,names):    
    '''Emit JIT output for consumption by the visualization
    Wrap the output in variable declaration and store into
    a file named facebook.rgraph.js for consumption by rgraph.html
    Write out another file that's standard JSON for additional analysis
    and potential use later
    '''    
    jit_output = []
    for fid in friendships:
        friendship = friendships[fid]
        adjacencies = friendship['friends']
        connections = '<br>'.join([names.get(a, 'Unknown') for a in adjacencies])
        normalized_popularity = 1.0 * len(adjacencies) / len(friendships)
        sex = friendship['sex']
        jit_output.append({
            'id': fid,
            'name': friendship['name'],
            'data': {'connections': connections, 'normalized_popularity'
                     : normalized_popularity, 'sex': sex},
                     'adjacencies': adjacencies,
                     })

    html = open(rgraphtemplate).read() %(json.dumps(jit_output),)
    f = open(rgraphfile, 'w')
    f.write(html)
    f.close()
    print >> sys.stderr, 'Data exported to file: {}'.format(f.name)
    #Saving JSON...
    json_f = open(dumpjson, 'w')
    json_f.write(json.dumps(jit_output, indent=4))
    json_f.close()
    print('Data exported to file: {}'.format(json_f.name))
    # Open up the web page in your browser
    #webbrowser.open('file://' + f.name)

def generate_rgraph_friends_bygroup():
    # Uses the previously saved JSON file
    rgraph = json.loads(open(dumpjson).read())
    groups = gapi.get_connections('me', 'groups')
    # Display groups and prompt the user
    for i in range(len(groups['data'])):
        print '%s) %s' %(i, groups['data'][i]['name'])
    choice = int(raw_input('Escolha um dos grupos para o grafico: '))
    gid = groups['data'][choice]['id']
    # Find the friends in the group
    fql = FQL(ACCESS_TOKEN)
    q = """select uid from group_member where gid = %s and uid in (select target_id\
    from connection where source_id = me() and target_type = 'user')"""%(gid, )
    uids = [u['uid'] for u in fql.query(q)]
    # Filter the previously generated output for these ids
    filtered_rgraph = [n for n in rgraph if n['id'] in uids]
    # Trim down adjancency lists for anyone not appearing in the graph.
    # Note that the full connection data displayed as HTML markup
    # in "connections" is still preserved for the global graph.
    for n in filtered_rgraph:
        n['adjacencies'] = [a for a in n['adjacencies'] if a in uids]
    html = open(rgraphtemplate).read() %(json.dumps(filtered_rgraph),)
    f = open(rgraphfile2, 'w')
    f.write(html)
    f.close()
    print('Data exported to file: {}'.format(f.name))
    # Open up the web page in your browser
    #webbrowser.open('file://' + f.name)
    
def gera_sungraph_friends():
    # Uses the previously saved JSON file
    data = json.loads(open(dumpjson).read())
    # Define colors to be used in the visualization
    # for aesthetics
    colors = ['#FF0000', '#00FF00', '#0000FF']

    # The primary output to collect input
    jit_output = {
        'id': 'friends',
        'name': 'friends',
        'data': {'$type': 'none'},
        'children': [],
        }
    # A convenience template
    template = {
        'id': 'friends',
        'name': 'friends',
        'data': {'connections': '', '$angularWidth': 1, '$color': ''},
        'children': [],
        }

    i = 0
    for g in ['male', 'female']:
        # Create a gender object
        go = deepcopy(template)
        go['id'] += '/' + g
        go['name'] += '/' + g
        go['data']['$color'] = colors[i]
        # Find friends by each gender
        friends_by_gender = [f for f in data if f['data']['sex'] == g]
        for f in friends_by_gender:
            # Load friends into the gender object
            fo = deepcopy(template)
            fo['id'] = f['id']
            fo['name'] = f['name']
            fo['data']['$color'] = colors[i % 3]
            fo['data']['$angularWidth'] = len(f['adjacencies'])  # Rank by global popularity
            fo['data']['connections'] = f['data']['connections'] # For the tooltip
            go['children'].append(fo)
        jit_output['children'].append(go)
        i += 1
    # Emit the output expected by the JIT Sunburst
    html = open(sunbursttemplate).read() %(json.dumps(jit_output),)
    f = open(sungraphfile, 'w')
    f.write(html)
    f.close()
    print('Data exported to file: {}'.format(f.name))
    # Open up the web page in your browser
    #webbrowser.open('file://' + f.name)

def weightTermByFreq(f, minfr,maxfr,minfo,maxfo):
    return (f - minfr) * (maxfo - minfo) / (maxfr - minfr) + minfo

def gera_tag_cloud():
    '''
    Implementation adapted from:
    http://help.com/post/383276-anyone-knows-the-formula-for-font-s
    '''
    BASE_URL = 'https://graph.facebook.com/me/home?access_token='
    NUM_PAGES = 10
    MIN_FREQUENCY = 2
    MIN_FONT_SIZE = 3
    MAX_FONT_SIZE = 30
    # Loop through the pages of connection data and build up messages
    url = BASE_URL + ACCESS_TOKEN
    messages = []
    current_page = 0
    while current_page < NUM_PAGES:
        data = json.loads(urllib2.urlopen(url).read())
        messages += [d['message'] for d in data['data'] if d.get('message')]
        current_page += 1
        url = data['paging']['next']
    # Compute frequency distribution for the terms
    fdist = nltk.FreqDist([term for m in messages for term in m.split()])
    # Customize a list of stop words as needed
    stop_words = nltk.corpus.stopwords.words('english')
    stop_words += nltk.corpus.stopwords.words('portuguese')
    stop_words += ['&', '.', '?', '!','...']
    # Create output for the WP-Cumulus tag cloud and sort terms by freq along the way
    raw_output = sorted([[escape(term), '', freq] for (term, freq) in fdist.items()
                        if freq > MIN_FREQUENCY and term not in stop_words],
                        key=lambda x: x[2])
    min_freq = raw_output[0][2]
    max_freq = raw_output[-1][2]
    weighted_output = [[i[0], i[1], weightTermByFreq(i[2], min_freq,max_freq,\
                        MIN_FONT_SIZE,MAX_FONT_SIZE)] for i in raw_output]
    # Substitute the JSON data structure into the template
    html_page = open(tagcloudtemplate).read() % (json.dumps(weighted_output), )
    f = open(graphcloudfile, 'w')
    f.write(html_page)
    f.close()
    print('Data exported to file: {}'.format(f.name))
    # Open up the web page in your browser
    # webbrowser.open('file://' + os.path.join(os.getcwd(), graphcloudfile))

def gera_planilha_friends():    
    # Reuses out/facebook.friends.json written out by 
    # facebook__get_friends_rgraph.py
    data = json.loads(open(dumpjson).read())
    popularity_data = [(f['name'], len(f['adjacencies'])) for f in data]
    popularity_data = sorted(popularity_data, key=operator.itemgetter(1))
    csv_data = []
    for d in popularity_data: 
        csv_data.append('{}\t{}'.format(d[0], d[1]))
    f = open(spreadsheet, 'w')
    f.write('\n'.join(csv_data))
    f.close()
    print('Data exported to file: {}'.format(f.name))
        
if __name__ == '__main__':
    #ACCESS_TOKEN = login()
    login()
    gapi = facebook.GraphAPI(ACCESS_TOKEN)
    
    '''Querying with Graph API
    http://developers.facebook.com/tools/explorer/'''
    find_groups('FGV')

    '''Queries com FQL
    http://developers.facebook.com/docs/reference/fql/'''
    fqlquery0 = "select name, sex, relationship_status from user WHERE uid = me()"    
    
    fqlquery1 = "select first_name, last_name, birthday from user WHERE uid IN \
    (select uid1 FROM friend WHERE uid2 = me())"  
    
    fqlquery2 = "select name, sex, relationship_status from user where uid in \
    (select target_id from connection where source_id = me() and target_type = 'user')"
    #Exemplo de multiquery FQL    
    
    fqlquery3 = """{"name_sex_relationships" : "select name, sex, relationship_status from user \
    where uid in (select target_id from #ids)","ids" : "select target_id from connection \
    where source_id = me() and target_type = 'user'"}"""
    
    fqlquery4 = "select target_id from connection where source_id = me() and target_type = 'user'"

    results = fql_queries(fqlquery4) #choose your query number or modify one
    print(json.dumps(result, indent=4))

    #my_friends_names = [str(t['first_name']+' '+str(t['last_name'])) for t in fql_queries(fqlquery1)]
    #my_friends_names = set(my_friends_names) #ordenar

    #my_friends_ids = [str(t['target_id']) for t in fql_queries(fqlquery4)]
    #fqlquery5 = "select uid1, uid2 from friend where uid1 in (%s) and uid2 in (%s)" \
    #%(",".join(my_friends_ids), ",".join(my_friends_ids),)
    #mutual_friendships = fql_queries(fqlquery5)
    
    #fqlquery6 = "select uid, first_name, last_name, sex from user where uid in (%s)" \
    #%(",".join(my_friends_ids),)
    #names = dict([(unicode(u["uid"]), u["first_name"] + " " +u["last_name"][0] + ".") for u in fql_queries(fqlquery6)])
    
    
    #friendships, names, sexes, mutual_friendships = graph_friends()
    #gera_rgraph_friends(friendships,names)
    #gera_sungraph_friends()
    #gera_rgraph_friends_bygroup()
    gera_tag_cloud()
    #gera_planilha_friends()