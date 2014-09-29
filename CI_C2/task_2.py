import pydelicious
import data_similarity
from util_pci import my_print

def initTagDict():
	sample_tags = ['programming', 'algorithm', 'productivity', 'facebook']
	tag_dict = {}
	all_urls = {}
	for tag in sample_tags:
		print 'Fecthing pop items...', tag
		tag_dict.setdefault(tag, {})
		tag_dict[tag] = getTagPopularUrls(tag)
		# mark all url
		for url in tag_dict[tag]:
			all_urls[url] = 1

	for tag in sample_tags:
		for url in all_urls:
			# mark value of un_related url as 0
			if url not in tag_dict[tag]:
				tag_dict[tag][url] = 0
	return tag_dict

def getTagPopularUrls(tag, n = 10):
	ret = {}
	for item in pydelicious.get_popular(tag = tag)[0:n]:
		ret[item['href']] = 1.0
	return ret

if __name__ == '__main__':
	tag_dict = initTagDict()
	my_print (tag_dict)
	my_print (data_similarity.topMatches(tag_dict, 'programming', simMethod = data_similarity.sim_euclid))
	my_print (data_similarity.getRecommendations(tag_dict, 'programming', simMethod = data_similarity.sim_euclid)[:10])
