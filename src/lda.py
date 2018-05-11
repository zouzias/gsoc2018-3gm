from __future__ import print_function
from time import time

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.datasets import fetch_20newsgroups
import parser
import collections
import numpy as np

no_features = 1000
no_top_words = 5

def display_topics(H, W, feature_names, data_samples, no_top_words, no_top_data_samples):
	graph = {}
	for topic_idx, topic in enumerate(H):
		print("Topic %d:" % (topic_idx))
		print(" ".join([feature_names[i]
						for i in topic.argsort()[:-no_top_words - 1:-1]]))
		top_doc_indices = np.argsort( W[:,topic_idx] )[::-1][0:no_top_data_samples]
		for doc_index in top_doc_indices:
			print(issues[doc_index].filename)
			graph[doc_index] = list ( filter( lambda x : x != doc_index,  top_doc_indices ))

	print(graph)		
	return graph

def bfs(graph, s):
	q = collections.deque()
	visited = collections.defaultdict(bool)
	q.append(s)
	print(q)
	while q:
		p = q.popleft()
		print(p)
		for r in graph[p]:
			if not visited[r]:
				q.append(r)
				visited[r] = True

greek_stopwords = []
cnt_swords = 300

with open('../data/el.dat') as f:
	for i in range(cnt_swords):
		line = f.readline()
		if not line:
			break
		line = line.split(' ')
		greek_stopwords.append(line[0])


issues, mdl = parser.generate_model_from_government_gazette_issues()
issues_dict = {}

data_samples = []

for i, issue in enumerate(issues):
	data_samples.append(''.join( issue.articles.values() ))
	issues_dict[i] = issue

n_samples = len(data_samples)
n_components = 10

words = []
for x in data_samples:
	words.extend(x.split(' '))

counter = collections.Counter(words)
gg_most_common = 300
for w in counter.most_common(gg_most_common):
	greek_stopwords.append(w[0])

# NMF is able to use tf-idf
tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words=greek_stopwords)
tfidf = tfidf_vectorizer.fit_transform(data_samples)
tfidf_feature_names = tfidf_vectorizer.get_feature_names()

# LDA can only use raw term counts for LDA because it is a probabilistic graphical model
tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words=greek_stopwords)
tf = tf_vectorizer.fit_transform(data_samples)
tf_feature_names = tf_vectorizer.get_feature_names()

no_topics = 10

# Run NMF
nmf_model = NMF(n_components=no_topics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)
nmf_W = nmf_model.transform(tfidf)
nmf_H = nmf_model.components_

# Run LDA
lda_model = LatentDirichletAllocation(n_components=no_topics, max_iter=5, learning_method='online', learning_offset=50.,random_state=0).fit(tf)
lda_W = lda_model.transform(tf)
lda_H = lda_model.components_

no_top_words = 5
no_top_data_samples = 3
display_topics(nmf_H, nmf_W, tfidf_feature_names, data_samples, no_top_words, no_top_data_samples)
display_topics(lda_H, lda_W, tf_feature_names, data_samples, no_top_words, no_top_data_samples)