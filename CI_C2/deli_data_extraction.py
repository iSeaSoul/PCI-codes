from pydelicious import get_popular, get_userposts, get_urlposts
import data_similarity
import time, random

def initUserDict(tag, count = 5):
	user_dict = {}
	for item in get_popular(tag = tag)[0:count]:
		for url_item in get_urlposts(item['href']):
			user_dict[url_item['user']] = {}
	return user_dict

RETRY_TM = 3
RETRY_WAITING_TM = 4

def fillItems(user_dict):
	all_items = {}
	for user in user_dict:
		for i in xrange(RETRY_TM):
			try:
				posts = get_userposts(user)
				break
			except:
				print 'Warn:: Failed in fetching user %s, retrying...' % (user, )
				time.sleep(RETRY_WAITING_TM)

		print 'Fetching user', user, posts
		for post in posts:
			url = post['href']
			# mark url of user as 1
			user_dict[user][url] = 1.0
			all_items[url] = 1

	for ratings in user_dict.values():
		for item in all_items:
			# mark url unreached by user as 0
			if item not in ratings:
				ratings[item] = 0.0

if __name__ == '__main__':
	user_dict = initUserDict('programming')
	fillItems(user_dict)
	print user_dict
	random_user = user_dict.keys()[random.randint(0, len(user_dict) - 1)]
	print data_similarity.topMatches(user_dict, random_user, simMethod = data_similarity.sim_euclid)
	recommend_urllist = data_similarity.getRecommendations(user_dict, random_user, simMethod = data_similarity.sim_euclid)
	trans_dict = data_similarity.transformPrefs(user_dict)
	print trans_dict
	print recommend_urllist[0][1], data_similarity.topMatches(trans_dict, recommend_urllist[0][1], simMethod = data_similarity.sim_euclid)
