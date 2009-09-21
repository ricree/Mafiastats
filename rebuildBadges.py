from Mafiastats.mafiaStats.signalHandlers import setColorBadge,BuildColorBadgeForPlayer
from Mafiastats.mafiaStats.models import Player

def buildBadges():
	img,fonts = setColorBadge()
	for p in Player.objects.all():
		print "Building badge for %s from %s"%(p.name,p.site.title)
		buildColorBadgeForPlayer(p,img,fonts)
	
