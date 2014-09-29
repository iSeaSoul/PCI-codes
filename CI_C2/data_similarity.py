from recommendations import critics
import math

def transformPrefs(prefs):
	# reverse dict
	ret = {}
	for person in prefs:
		for item in prefs[person]:
			ret.setdefault(item, {})
			ret[item][person] = prefs[person][item]
	return ret

def sim_euclid(prefs, person1, person2):
	# collect common items
	common_items = [item for item in prefs[person1] if item in prefs[person2]]
	if len(common_items) == 0:
		return 0

	#calculate sum of euclid distance
	e_sqrdist = sum([pow(prefs[person1][item] - prefs[person2][item], 2) for item in common_items])
	return 1 / (1 + math.sqrt(e_sqrdist))

def sim_pearson(prefs, person1, person2):
	# collect common items
	common_items = [item for item in prefs[person1] if item in prefs[person2]]
	n = len(common_items)
	if n == 0:
		return 0

	self_func = lambda x : x
	sqr_func = lambda x : x * x
	sum_func = lambda name, func: sum([func(prefs[name][item]) for item in common_items])

	sum1 = sum_func(person1, self_func)
	sum2 = sum_func(person2, self_func)
	sum_sqr1 = sum_func(person1, sqr_func)
	sum_sqr2 = sum_func(person2, sqr_func)

	sum_p = sum([prefs[person1][item] * prefs[person2][item] for item in common_items])

	#calculate sum of pearson score
	num = sum_p - sum1 * sum2 / n
	den = math.sqrt((sum_sqr1 - sqr_func(sum1) / n) * (sum_sqr2 - sqr_func(sum2) / n))

	if den < 1e-8 and den > -1e-8: return 0
	return num / den

def calcSimilarityItems(prefs, n = 10, simMethod = sim_euclid):
	ret = {}
	cnt = 0
	itemPrefs = transformPrefs(prefs)
	for item in itemPrefs:
		cnt += 1
		if cnt % 100 == 0:
			print 'Processing... %d / %d' %  (cnt, len(itemPrefs))
		ret[item] = topMatches(itemPrefs, item, topN = n, simMethod = simMethod)
	return ret

def topMatches(prefs, person, topN = 3, simMethod = sim_pearson):
	scores = [(simMethod(prefs, person, other), other) for other in prefs if other != person]
	scores.sort()
	scores.reverse()
	topN = min(len(scores), topN)

	return scores[0:topN]

def getRecommendations(prefs, person, simMethod = sim_pearson):
	sum_scores = {}
	sum_sims = {}

	for otherp in prefs:
		if otherp == person:
			continue

		sim = simMethod(prefs, person, otherp)
		if sim <= 1e-8: continue

		for item in prefs[otherp]:
			if item in prefs[person] and prefs[person][item] != 0: continue
			sum_scores.setdefault(item, 0)
			sum_sims.setdefault(item, 0)
			sum_scores[item] += sim * prefs[otherp][item]
			sum_sims[item] += sim

	rankings = [(scores / sum_sims[item], item) for item, scores in sum_scores.items()]
	rankings.sort()
	rankings.reverse()

	return rankings

def getRecommendedItems(prefs, itemMatchDict, person):
	sum_scores = {}
	sum_sims = {}

	for item, rating in prefs[person].items():
		for simi, otheri in itemMatchDict[item]:
			if otheri in prefs[person]: continue

			sum_scores.setdefault(otheri, 0)
			sum_sims.setdefault(otheri, 0)
			sum_scores[otheri] += simi * rating
			sum_sims[otheri] += simi

	rankings = [(scores / sum_sims[item], item) for item, scores in sum_scores.items()]
	rankings.sort()
	rankings.reverse()

	return rankings

if __name__ == '__main__':
	print sim_euclid(critics, 'Lisa Rose', 'Gene Seymour')
	print sim_pearson(critics, 'Lisa Rose', 'Gene Seymour')
	print topMatches(critics, 'Toby')
	print getRecommendations(critics, 'Toby', simMethod = sim_euclid)

	item_dict = calcSimilarityItems(critics)
	print item_dict
	print getRecommendedItems(critics, item_dict, 'Toby')