from Mafiastats.mafiaStats.models import Site, Game, Team, Category,Player
from django.db.models.query import QuerySet


def attrSort(items,attr,reverse):
	print str(reverse)
	return sorted(items,(lambda x,y: cmp(getattr(x,attr),getattr(y,attr))),reverse=reverse)


def sortQuery(query,sortMethod,reverse):
	"""Returns a sorted queryset Will use sort_by if sortMethod is a string 	Will pass a sequence pulled from query if sortMethod is callable"""
	print "I GOT CALLED"
	if(type(sortMethod) is str):
		print 'str sort'
		if type(query) is QuerySet:
			if reverse:
				sortMethod = '-'+sortMethod
			return query.order_by(sortMethod)
		else:
			print 'list sort'
			return attrSort(query,sortMethod,reverse)
	items = query.all() if type(query) is QuerySet else query
	if(hasattr(sortMethod,'__call__')):
		return sortMethod(items,reverse)


def playersByWins(players,reverse):
	return sorted(players,(lambda x,y:cmp(x.wins(),y.wins())),reverse=reverse)

def playersByLosses(players,reverse):
	return sorted(players,(lambda x,y:cmp(x.losses(),y.losses())),reverse=reverse)

def playersByWinPct(players,reverse):
	return sorted(players,(lambda x,y:cmp(x.winPct(),y.winPct())),reverse=reverse)

def playersByModerated(players,reverse):
	return sorted(players,(lambda x,y:cmp(x.modded(),y.modded())),reverse=reverse)
