from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
	(r'^site/(?P<site_id>\d+)/$', 'mafiaStats.views.site'),
	(r'^site/(?P<site_id>\d+)/scoreboard/$','mafiaStats.views.scoreboard'),
	(r'^site/(?P<site_id>\d+)/games/$','mafiaStats.views.games'),
	(r'^site/(?P<site_id>\d+)/moderators/$','mafiaStats.views.moderators'),
	(r'^game/add/(?P<site_id>\d*)/*$','mafiaStats.views.add'),
	(r'^game/(?P<game_id>\d+)/$','mafiaStats.views.game'),
	(r'^player/(?P<player_id>\d+)/$','mafiaStats.views.player'),
	(r'^player/(?P<player_id>\d+)/played/$','mafiaStats.views.playerPlayed'),
	(r'^player/(?P<player_id>\d+)/moderated/$','mafiaStats.views.playerModerated'),
	(r'^player/name_lookup','mafiaStats.views.nameLookup'),
	(r'^game/(?P<game_id>\d+)/edit$','mafiaStats.views.edit'),
	)
