from django.conf.urls.defaults import *
from django.conf import settings

from mafiaStats import views

urlpatterns = patterns('',
	(r'^site/(?P<site_id>\d+)/$', 'Mafiastats.mafiaStats.views.site'),
	(r'^site/(?P<site_id>\d+)/scoreboard/$','Mafiastats.mafiaStats.views.scoreboard'),
	(r'^site/(?P<site_id>\d+)/games/$','Mafiastats.mafiaStats.views.games'),
	(r'^site/(?P<site_id>\d+)/moderators/$','Mafiastats.mafiaStats.views.moderators'),
	(r'^game/add/(?P<site_id>\d*)/*$','Mafiastats.mafiaStats.views.add'),
	(r'^game/(?P<game_id>\d+)/$','Mafiastats.mafiaStats.views.game'),
	(r'^player/(?P<player_id>\d+)/$','Mafiastats.mafiaStats.views.player'),
	(r'^player/(?P<player_id>\d+)/played/$','Mafiastats.mafiaStats.views.playerPlayed'),
	(r'^player/(?P<player_id>\d+)/moderated/$','Mafiastats.mafiaStats.views.playerModerated'),
	(r'^player/name_lookup','Mafiastats.mafiaStats.views.nameLookup'),
	)
