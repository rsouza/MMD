# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime as dt
import json
import feedparser
import numpy
from BeautifulSoup import BeautifulStoneSoup
import nltk
from nltk import clean_html, ingrams, FreqDist

# Trechos de Codigo adaptados de blogs_and_nlp__get_feed, blogs_and_nlp__sentence_detection.py, 
# blogs_and_nlp__summarize.py, blogs_and_nlp__summarize_markedup_output.py,
# blogs_and_nlp__extract_entities.py, blogs_and_nlp__extract_interactions.py
# blogs_and_nlp__extract_interactions_markedup_output.py

datapath = "/home/rsouza/Dropbox/Renato/Python/MMD/"
jfile = 'feed.json'
mfile = 'summaryfeed.html'
jsonfile = (datapath+jfile)
markedhtmlfile = (datapath+mfile)
feed_url = 'http://feeds.feedburner.com/oreilly/radar/atom'

stop_words = nltk.corpus.stopwords.words('english')
ignore_words = [".",",","--","'s","?",")","(",":","'","'re",'"',"-","}","{"]
ignorelist = stop_words+ignore_words

HTML_TEMPLATE = """<html>
    <head>
        <title>%s</title>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    </head>
    <body>%s</body>
</html>"""

def cleanHtml(html):
    return BeautifulStoneSoup(clean_html(html),
                              convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]

def get_feed(feed):
    fp = feedparser.parse(feed_url)
    print "Recuperadas %s entradas de '%s'" % (len(fp.entries[0].title), fp.feed.title)
    blog_posts = []
    for e in fp.entries:
        blog_posts.append({'title': e.title, 'content'
                          : cleanHtml(e.content[0].value), 'link': e.links[0].href})
    f = open(jsonfile, 'w')
    f.write(json.dumps(blog_posts))
    f.close()
    print >> sys.stderr, 'Conteudo salvo em: %s' % (f.name, )

def sentence_detection():
    blog_data = json.loads(open(jsonfile).read())    
    for post in blog_data:
        sentences = nltk.tokenize.sent_tokenize(post['content'])
        words = [w.lower() for sentence in sentences for w in
                 nltk.tokenize.word_tokenize(sentence)]
        fdist = nltk.FreqDist(words)
        # Basic stats
        num_words = sum([i[1] for i in fdist.items()])
        num_unique_words = len(fdist.keys())
        # Hapaxes are words that appear only once
        num_hapaxes = len(fdist.hapaxes()) #palavras que so aparecem uma vez
        top_10_words_sans_stop_words = [w for w in fdist.items() if w[0]
                                        not in ignorelist][:10]
        print post['title']
        print '\tNum Sentences:'.ljust(25), len(sentences)
        print '\tNum Words:'.ljust(25), num_words
        print '\tNum Unique Words:'.ljust(25), num_unique_words
        print '\tNum Hapaxes:'.ljust(25), num_hapaxes
        print '\tTop 10 Most Frequent Words (sans stop words):\n\t\t', \
                '\n\t\t'.join(['%s (%s)'
                % (w[0], w[1]) for w in top_10_words_sans_stop_words])
        print

def score_sentences(sentences, important_words):
    # Approach taken from "The Automatic Creation of Literature Abstracts" by H.P. Luhn
    CLUSTER_THRESHOLD = 5  # Distance between words to consider
    scores = []
    sentence_idx = -1
    for s in [nltk.tokenize.word_tokenize(s) for s in sentences]:
        sentence_idx += 1
        word_idx = []
        # For each word in the word list...
        for w in important_words:
            try:
                # Compute an index for where any important words occur in the sentence
                word_idx.append(s.index(w))
            except ValueError, e: # w not in this particular sentence
                pass
        word_idx.sort()
        # It is possible that some sentences may not contain any important words at all
        if len(word_idx)== 0: continue
        # Using the word index, compute clusters by using a max distance threshold
        # for any two consecutive words
        clusters = []
        cluster = [word_idx[0]]
        i = 1
        while i < len(word_idx):
            if word_idx[i] - word_idx[i - 1] < CLUSTER_THRESHOLD:
                cluster.append(word_idx[i])
            else:
                clusters.append(cluster[:])
                cluster = [word_idx[i]]
            i += 1
        clusters.append(cluster)
        # Score each cluster. The max score for any given cluster is the score 
        # for the sentence
        max_cluster_score = 0
        for c in clusters:
            significant_words_in_cluster = len(c)
            total_words_in_cluster = c[-1] - c[0] + 1
            score = 1.0 * significant_words_in_cluster \
                * significant_words_in_cluster / total_words_in_cluster
            if score > max_cluster_score:
                max_cluster_score = score
        scores.append((sentence_idx, score))
    return scores

def summarize(txt):
    TOP_SENTENCES = 5  # Numero de sentencas a escolher no sumario "top n"
    N = 100  # Numero de palavras a considerar
    sentences = [s for s in nltk.tokenize.sent_tokenize(txt)]
    normalized_sentences = [s.lower() for s in sentences]
    words = [w.lower() for sentence in normalized_sentences for w in
             nltk.tokenize.word_tokenize(sentence)]
    fdist = nltk.FreqDist(words)
    top_n_words = [w[0] for w in fdist.items() 
            if w[0] not in nltk.corpus.stopwords.words('english')][:N]
    scored_sentences = score_sentences(normalized_sentences, top_n_words)
    # Primeira abordagem: 
    # Filter out non-significant sentences by using the average score plus a
    # fraction of the std dev as a filter
    avg = numpy.mean([s[1] for s in scored_sentences])
    std = numpy.std([s[1] for s in scored_sentences])
    mean_scored = [(sent_idx, score) for (sent_idx, score) in scored_sentences
                   if score > avg + 0.5 * std]
    # Segunda abordagem: 
    # Another approach would be to return only the top N ranked sentences
    top_n_scored = sorted(scored_sentences, key=lambda s: s[1])[-TOP_SENTENCES:]
    top_n_scored = sorted(top_n_scored, key=lambda s: s[0])
    # Decorate the post object with summaries
    return dict(top_n_summary=[sentences[idx] for (idx, score) in top_n_scored],
                mean_scored_summary=[sentences[idx] for (idx, score) in mean_scored])

def show_summaries():
    blog_data = json.loads(open(jsonfile).read())    
    for post in blog_data:
        post.update(summarize(post['content']))
        print post['title']
        print '-' * len(post['title'])
        print
        print '-------------'
        print 'Top N Summary'
        print '-------------'
        print ' '.join(post['top_n_summary'])
        print
        print '-------------------'
        print 'Mean Scored Summary'
        print '-------------------'
        print ' '.join(post['mean_scored_summary'])
        print

def save_html_summaries():
    if not os.path.isdir('out/summarize'):
        os.makedirs('out/summarize')
    blog_data = json.loads(open(jsonfile).read())    
    for post in blog_data:
        post.update(summarize(post['content']))
        # You could also store a version of the full post with key sentences markedup
        # for analysis with simple string replacement...
        for summary_type in ['top_n_summary', 'mean_scored_summary']:
            post[summary_type + '_marked_up'] = '<p>%s</p>' % (post['content'], )
            for s in post[summary_type]:
                post[summary_type + '_marked_up'] = \
                post[summary_type + '_marked_up'].replace(s, '<strong>%s</strong>' % (s, ))
            filename = post['title'] + '.summary.' + summary_type + '.html'
            f = open(os.path.join('out', 'summarize', filename), 'w')
            #f = open(markedhtmlfile, 'w')
            html = HTML_TEMPLATE % (post['title'] + ' Summary', post[summary_type + '_marked_up'],)
            f.write(html.encode('utf-8'))
            f.close()
            print >> sys.stderr, "Conteudo salvo em: ", f.name

def extract_entities():
    blog_data = json.loads(open(jsonfile).read())
    for post in blog_data:
        sentences = nltk.tokenize.sent_tokenize(post['content'])
        tokens = [nltk.tokenize.word_tokenize(s) for s in sentences]
        pos_tagged_tokens = [nltk.pos_tag(t) for t in tokens]
        # Flatten the list since we're not using sentence structure
        # and sentences are guaranteed to be separated by a special
        # POS tuple such as ('.', '.')
        pos_tagged_tokens = [token for sent in pos_tagged_tokens for token in sent]
        all_entity_chunks = []
        previous_pos = None
        current_entity_chunk = []
        for (token, pos) in pos_tagged_tokens:
            if pos == previous_pos and pos.startswith('NN'):
                current_entity_chunk.append(token)
            elif pos.startswith('NN'):
                if current_entity_chunk != []:
                    # Note that current_entity_chunk could be a duplicate when appended,
                    # so frequency analysis again becomes a consideration
                     all_entity_chunks.append((' '.join(current_entity_chunk), pos))
                current_entity_chunk = [token]
            previous_pos = pos
        # Store the chunks as an index for the document
        # and account for frequency while we're at it...
        post['entities'] = {}
        for c in all_entity_chunks:
            post['entities'][c] = post['entities'].get(c, 0) + 1
        # For example, we could display just the title-cased entities
        print post['title']
        print '-' * len(post['title'])
        proper_nouns = []
        for (entity, pos) in post['entities']:
            if entity.istitle():
                print '\t%s (%s)' % (entity, post['entities'][(entity, pos)])
        print

def extract_interactions(txt):
    sentences = nltk.tokenize.sent_tokenize(txt)
    tokens = [nltk.tokenize.word_tokenize(s) for s in sentences]
    pos_tagged_tokens = [nltk.pos_tag(t) for t in tokens]
    entity_interactions = []
    for sentence in pos_tagged_tokens:
        all_entity_chunks = []
        previous_pos = None
        current_entity_chunk = []
        for (token, pos) in sentence:
            if pos == previous_pos and pos.startswith('NN'):
                current_entity_chunk.append(token)
            elif pos.startswith('NN'):
                if current_entity_chunk != []:
                    all_entity_chunks.append((' '.join(current_entity_chunk),
                            pos))
                current_entity_chunk = [token]
            previous_pos = pos
        if len(all_entity_chunks) > 1:
            entity_interactions.append(all_entity_chunks)
        else:
            entity_interactions.append([])
    assert len(entity_interactions) == len(sentences)
    return dict(entity_interactions=entity_interactions,
                sentences=sentences)

def show_interactions():
    blog_data = json.loads(open(jsonfile).read())
    for post in blog_data:
        post.update(extract_interactions(post['content']))
        print post['title']
        print '-' * len(post['title'])
        for interactions in post['entity_interactions']:
            print '; '.join([i[0] for i in interactions])
        print

def save_html_interactions():
    blog_data = json.loads(open(jsonfile).read())
    if not os.path.isdir('out/interactions'):
        os.makedirs('out/interactions')
    for post in blog_data:
        post.update(extract_interactions(post['content']))
        # Display output as markup with entities presented in bold text
        post['markup'] = []
        for sentence_idx in range(len(post['sentences'])):
            s = post['sentences'][sentence_idx]
            for (term, _) in post['entity_interactions'][sentence_idx]:
                s = s.replace(term, '<strong>%s</strong>' % (term, ))
            post['markup'] += [s]
        filename = post['title'] + '.entity_interactions.html'
        f = open(os.path.join('out', 'interactions', filename), 'w')
        html = HTML_TEMPLATE % (post['title'] + ' Interactions', ' '.join(post['markup']),)
        f.write(html.encode('utf-8'))
        f.close()
        print >> sys.stderr, "Conteudo salvo em: ", f.name

if __name__ == '__main__':
    get_feed(feed_url)
    #sentence_detection()
    #show_summaries()
    #save_html_summaries()
    #extract_entities()
    #show_interactions()
    #save_html_interactions()