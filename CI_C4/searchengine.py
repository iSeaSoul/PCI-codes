import sqlite3, urllib2, re
import BeautifulSoup as bs
from urlparse import urljoin

ignorewords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])

class crawler( object ):

	def __init__(self, dbname):
		self.con = sqlite3.connect(dbname)

	def __del__(self):
		self.con.close()

	def dbcommit(self):
		self.con.commit()

	# Auxilliary function for getting an entry id
	# if it's not present, add a new
	def getentryid(self, table, field, value, createnew = True):
		cur = self.con.execute('SELECT rowid FROM %s WHERE %s = ?' % (table, field), (value, ))
		res = cur.fetchone()
		if res == None:
			cur = self.con.execute('INSERT INTO %s(%s) values(?)' % (table, field), (value, ))
			return cur.lastrowid
		else:
			return res[0]

	# Index an individual page
	def addtoindex(self, url, soup):
		if self.isindexed(url): 
			return

		print 'Indexing %s' % url
		text = self.gettextonly(soup)
		words = self.separatewords(text)
		urlid = self.getentryid('urllist', 'url', url)

		for idx in xrange(len(words)):
			word = words[idx]
			if word in ignorewords: return
			wordid = self.getentryid('wordlist', 'word', word)
			self.con.execute('INSERT INTO wordlocation(urlid, wordid, location) values(?, ?, ?)',
				(urlid, wordid, idx))

	# Extract the text from an HTML page (no tags)
	def gettextonly(self, soup):
		v = soup.string
		if v == None:
			c = soup.contents
			rettext = ''
			for t in c:
				subtext = self.gettextonly(t)
				rettext += subtext + '\n'
			return rettext
		else:
			return v.strip()

	# Separate the words by any non-whitespace character
	def separatewords(self, text):
		splitregex = re.compile(r'\W*')
		return [s.lower() for s in splitregex.split(text) if s != '']

	# Return true if this url is already indexed
	def isindexed(self, url):
		cur = self.con.execute('SELECT rowid FROM urllist WHERE url = ?', (url, ))
		res = cur.fetchone()
		if res == None:
			return False
		cur = self.con.execute('SELECT * FROM wordlocation WHERE urlid = ?', (res[0], ))
		res = cur.fetchone()
		return res != None

	# Add a link between two pages
	def addlinkref(self, urlFrom, urlTo, linkText):
		pass

	# Starting with a list of pages, do a breadth
	# first search to the given depth, indexing pages
	# as we go
	def crawl(self, pages, depth = 2):
		for tm in xrange(depth):
			newpages = set()
			for page in pages:
				try:
					c = urllib2.urlopen(page)
				except:
					print 'ERROR:: cannot open %s' % (page, )
					continue
				soup = bs.BeautifulSoup(c.read())
				self.addtoindex(page, soup)

				# crawl all links
				links = soup('a')
				for link in links:
					if 'href' in dict(link.attrs):
						url = urljoin(page, link['href'])
						if url.find("'") != -1: continue
						url=url.split('#')[0] # remove location portion
						if url[0:4]=='http' and not self.isindexed(url):
							newpages.add(url)
						linkText = self.gettextonly(link)
						self.addlinkref(page, url, linkText)

				self.dbcommit()

			pages=newpages

	# Create the database tables
	def createindextables(self):
		self.con.execute('create table urllist(url)')
		self.con.execute('create table wordlist(word)')
		self.con.execute('create table wordlocation(urlid, wordid, location)')
		self.con.execute('create table link(fromid integer,toid integer)')
		self.con.execute('create table linkwords(wordid, linkid)')
		self.con.execute('create index wordidx on wordlist(word)')
		self.con.execute('create index urlidx on urllist(url)')
		self.con.execute('create index wordurlidx on wordlocation(wordid)')
		self.con.execute('create index urltoidx on link(toid)')
		self.con.execute('create index urlfromidx on link(fromid)')
		self.dbcommit()

if __name__ == '__main__':
	cl = crawler('db_pages.db')
	# cl.createindextables()
	# cl.crawl(['http://raindreamer.diandian.com/'])
	print [row for row in cl.con.execute('select rowid from wordlocation where wordid=1')]