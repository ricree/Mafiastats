from Mafiastats.mafiaStats.models import Site, Game, Team, Category,Player


def sortQuery(query,sortMethod,reverse):
	"""Returns a sorted queryset Will use sort_by if sortMethod is a string 	Will pass a sequence pulled from query if sortMethod is callable"""
	if(type(sortMethod) is str):
		if reverse:
			sortMethod = '-'+sortMethod
		return query.order_by(sortMethod)
	if(hasattr(sortMethod,'__call__')):
		return sortMethod(query.all(),reverse)


def playersByWins(players,reverse):
	return sorted(players,(lambda x,y:cmp(x.wins(),y.wins())),reverse=reverse)

def playersByLosses(players,reverse):
	return sorted(players,(lambda x,y:cmp(x.losses(),y.losses())),reverse=reverse)

def playersByWinPct(players,reverse):
	return sorted(players,(lambda x,y:cmp(x.winPct(),y.winPct())),reverse=reverse)

def playersByModerated(players,reverse):
	return sorted(players,(lambda x,y:cmp(x.moderated_set.count(),y.moderated_set.count())),reverse=reverse)
