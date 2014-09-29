import sys
sys.path.append('..')

import CI_C2.feedparser as feedparser
from CI_C2.util_pci import my_print
import re, json

def getWordCounts(url):
	d = feedparser.parse(url)
	word_count = {}

	for e in d.entries:
		summary = e.summary if 'summary' in e else e.description

		for word in getWords(e.title + ' ' + summary):
			word_count.setdefault(word, 0)
			word_count[word] += 1

	return d.feed.title, word_count

def getWords(contents):
	# replace all html tags
	txt = re.compile(r'<[^>]+>').sub('', contents)

	# split
	words = re.compile(r'[^a-zA-Z]+').split(txt)

	# lower all
	return [word.lower() for word in words if word != '']

def genBigData():
	apcount = {}
	wordcounts = {}
	feedlist = [line.strip() for line in file('feedlist.txt')]
	for feedurl in feedlist:
		try:
			print 'Parsing', feedurl, '...'
			title, wc = getWordCounts(feedurl)
			wordcounts[title] = wc
			for word, count in wc.items():
				apcount.setdefault(word,0)
				if count > 1:
					apcount[word] += 1
		except:
			print 'Failed to parse', feedurl

	wordlist = []
	for w, bc in apcount.items( ):
		if 1 < bc < 5:
			wordlist.append(w)

	out = file('blogdata_l.txt','w')
	out.write('Blog')
	for word in wordlist: 
		out.write('\t%s' % word)
	out.write('\n')
	for blog, wc in wordcounts.items( ):
		out.write(blog.encode('utf8', 'ignore'))
		for word in wordlist:
			if word in wc: out.write('\t%d' % wc[word])
			else: out.write('\t0')
		out.write('\n')

if __name__ == '__main__':
	genBigData()
	# title, wc = getWordCounts('http://iseasoul.diandian.com/rss')
	# print type(title)
	# print title.encode('utf8', 'ignore')
	# my_print (wc)