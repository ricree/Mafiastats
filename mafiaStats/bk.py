def levenshtein(s1, s2):
	if hasattr(s1,'__iter__'):
		s1 = s1[0]
	if hasattr(s1,'__iter__'):
		s2 = s2[0]
	if len(s1) < len(s2):
		return levenshtein(s2, s1)
	if not s1:
		return len(s2)
 
	previous_row = xrange(len(s2) + 1)
	for i, c1 in enumerate(s1):
		current_row = [i + 1]
		for j, c2 in enumerate(s2):
			insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
			deletions = current_row[j] + 1	   # than s2
			substitutions = previous_row[j] + (c1 != c2)
			current_row.append(min(insertions, deletions, substitutions))
		previous_row = current_row
 
	return previous_row[-1]


class BKTree(object):
	root = None
	def __getitem__(self,key):
		word,d = key
		return self.getItems(word,d,self.root,0)
		
	def getItems(self,word,d,node,level):
		if node == None:
			return
		rt, nodes = node
		n = levenshtein(word,rt)
		if n <= d:
			yield rt
		if nodes != None:
			for i in range(n-d,n+d+1):
				if i in nodes:
					results = self.getItems(word,d,nodes[i],i+1)
					for x in results:
						yield x
				

	def addItem(self,node, item):
		if node == None:
			return (item, None)
		rt, nodes = node
		d = levenshtein(item,rt)
		if not nodes:
			nodes = {}
			current = None
		elif d in nodes:
			current = nodes[d]
		else:
			current = None
		nodes[d] = self.addItem(current,item)
		return (rt,nodes)
	def add(self,item):
		self.root = self.addItem(self.root,item)
