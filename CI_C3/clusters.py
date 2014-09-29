import math, random

def readfile(filename):
	lines = [line.strip() for line in file(filename)]
	col_names = lines[0].split('\t')[1:]
	row_names = []
	vec_data = []
	for line in lines[1:]:
		line_items = line.split('\t')
		row_names.append(line_items[0])
		vec_data.append([float(num) for num in line_items[1:]])
	return row_names, col_names, vec_data

def transformVec(data):
	ret = []
	if not data: return ret
	for i in xrange(len(data[0])):
		row_data = [data[j][i] for j in xrange(len(data))]
		ret.append(row_data)
	return ret

def sim_tanimoto(vec1, vec2):
	# radio of intersection set
	c1, c2, common = 0, 0, 0
	for idx in xrange(len(vec1)):
		if vec1[idx] != 0: c1 += 1
		if vec2[idx] != 0: c2 += 1
		if vec1[idx] != 0 and vec2[idx] != 0: common += 1

	return 1.0 - 1.0 * common / (c1 + c2 - common)

def sim_pearson(vec1, vec2):
	assert (len(vec1) == len(vec2))

	self_func = lambda x : x
	sqr_func = lambda x : x * x
	sum_func = lambda items, func: sum([func(item) for item in items])

	n = len(vec1)
	sum1 = sum_func(vec1, self_func)
	sum2 = sum_func(vec2, self_func)
	sum_sqr1 = sum_func(vec1, sqr_func)
	sum_sqr2 = sum_func(vec2, sqr_func)

	sum_p = sum([vec1[i] * vec2[i] for i in xrange(n)])

	# calculate sum of pearson score
	num = sum_p - sum1 * sum2 / n
	den = math.sqrt((sum_sqr1 - sqr_func(sum1) / n) * (sum_sqr2 - sqr_func(sum2) / n))

	if den < 1e-8 and den > -1e-8: return 0
	return 1.0 - num / den

class clusterNode(object):
	def __init__(self, vec, id = None, left = None, right = None, dis = 0.0):
		self.vec = vec
		self.id = id
		self.left = left
		self.right = right
		self.dis = dis

def buildCluster(data, distance = sim_pearson):
	# init cluster node
	clust = [clusterNode(data[idx], id = idx) for idx in xrange(len(data))]
	next_cn_id = -1
	dis_dict = {}

	# build binary tree
	while len(clust) > 1:
		min_dist = distance(clust[0].vec, clust[1].vec)
		min_dist_pair = (1, 0)

		for i in xrange(len(clust)):
			for j in xrange(i):
				if (clust[i].id, clust[j].id) not in dis_dict:
					dis_dict[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec)

				cur_dist = dis_dict[(clust[i].id, clust[j].id)]
				if cur_dist < min_dist:
					min_dist = cur_dist
					min_dist_pair = (i, j)

		merged_vec = [(clust[min_dist_pair[0]].vec[i] + clust[min_dist_pair[1]].vec[i]) / 2
			for i in xrange(len(clust[min_dist_pair[0]].vec))]

		new_cluster_node = clusterNode(merged_vec, left = clust[min_dist_pair[0]], 
			right = clust[min_dist_pair[1]], dis = min_dist, id = next_cn_id)

		# delete old & append new
		next_cn_id -= 1
		del clust[min_dist_pair[0]]
		del clust[min_dist_pair[1]]
		clust.append(new_cluster_node)

	# root node
	return clust[0]

def printClusterTree(root, names, indent_num = 0):
	for i in xrange(indent_num): print ' ',
	if root.id < 0:
		print '-'
	else:
		print names[root.id] if names else root.id

	if root.left:
		printClusterTree(root.left, names, indent_num + 1)
	if root.right:
		printClusterTree(root.right, names, indent_num + 1)

def getRandomNumber(lower, upper):
	return random.random() * (upper - lower) + lower

MAX_ITERTAE_TM = 100

def kMeansCluster(data, k = 3, distance = sim_pearson):
	if not data or not k:
		return []

	# random K centre
	random_range = [(min([row[i] for row in data]), max([row[i] for row in data]))
		for i in xrange(len(data[0]))]

	cluster_centre = []
	for i in xrange(k):
		cluster_centre.append([getRandomNumber(random_range[i][0], random_range[i][1]) 
			for i in xrange(len(random_range))])

	last_cret = None
	avg_func = lambda vals: 0 if len(vals) == 0 else sum(vals) / len(vals)

	for tm in xrange(MAX_ITERTAE_TM):
		print 'Iteration', tm, '...'

		best_cret = [[] for i in xrange(k)]
		for idx in xrange(len(data)):
			min_dist = distance(cluster_centre[0], data[idx])
			min_dist_idx = 0
			for i in xrange(1, k):
				cur_dist = distance(cluster_centre[i], data[idx])
				if cur_dist < min_dist:
					min_dist = cur_dist
					min_dist_idx = i
			best_cret[min_dist_idx].append(idx)

		# no change, break
		if best_cret == last_cret:
			break
		last_cret = best_cret

		for i in xrange(k):
			cluster_centre[i] = [avg_func([data[idx][idy] for idx in last_cret[i]]) 
				for idy in xrange(len(data[0]))]

	return last_cret

def printKMeansCluster(clist, name):
	for sublist in clist:
		print '[',
		for idx in sublist:
			print name[idx] + ',', 
		print ']'

if __name__ == '__main__':
	names, words, data = readfile('blogdata_l.txt')
	# clust = buildCluster(data)
	# printClusterTree(clust, names)
	# clust_word = buildCluster(transformVec(data))
	# printClusterTree(clust_word, words)

	klust = kMeansCluster(data)
	printKMeansCluster(klust, names)