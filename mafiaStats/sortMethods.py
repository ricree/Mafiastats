from Mafiastats.mafiaStats.models import Site, Game, Team, Category,Player


def sortQuery(query,sortMethod,reverse):
	"""Returns a sorted queryset Will use sort_by if sortMethod is a string 	Will pass a sequence pulled from query if sortMethod is callable"""
	if(type(sortMethod) is str):
		if reverse:
			sortMethod = '-'+sortMethod
		return query.sort_by(sortMethod)
	if(hasattr(sortMethod,'__call__')):
		return sortMethod(query.all())


def playersByWins(players,reverse):
	return sorted(players,lambda x,y:cmp(x.wins(),y.wins()) if reverse else cmp(y.wins(),x.wins()))

def playersByLosses(players,reverse):
	return sorted(players,lambda x,y:cmp(x.losses(),y.losses()) if reverse else cmp(y.loses(),x.losses()))
