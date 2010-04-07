from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
	url(r'^site/(?P<site_id>\d*)/$', 'mafiaStats.views.site',name='mafiastats_site'),
	url(r'^site/scoreboard/(?P<site_id>\d*)/*$','mafiaStats.views.scoreboard',name='mafiastats_scoreboard'),
	url(r'^site/scoreboard/(?P<site_id>\d*)/(?P<category>\d*)/*$','mafiaStats.views.scoreboard',name='mafiastats_scoreboard_typed'),
	url(r'^site/games/(?P<site_id>\d*)','mafiaStats.views.games',name='mafiastats_games'),
	url(r'^site/moderators/(?P<site_id>\d*)','mafiaStats.views.moderators',name='mafiastats_moderators'),
	url(r'^player/(?P<player_id>\d*)/graph/','mafiaStats.views.playerGraph',name='mafiastats_player_graph'),
	url(r'^game/add/(?P<site_id>\d*)/*$','mafiaStats.views.add',name='mafiastats_add'),
	url(r'^game/(?P<game_id>\d+)/$','mafiaStats.views.game',name='mafiastats_game'),
	url(r'^game/name_lookup/$','mafiaStats.views.game_name_lookup', name="mafiastats_game_name_lookup"),
	url(r'^game/lookup/$','mafiaStats.views.game_lookup',name="mafiastats_game_lookup"),
	url(r'^player/(?P<player_id>\d+)/$','mafiaStats.views.player',name='mafiastats_player'),
	url(r'^player/lookup/$','mafiaStats.views.player_lookup', name='mafiastats_player_lookup'),
	url(r'^player/(?P<player_id>\d+)/played/$','mafiaStats.views.playerPlayed',name='mafiastats_played'),
 	url(r'^player/(?P<player_id>\d+)/moderated/$','mafiaStats.views.playerModerated',name='mafiastats_moderated'),
	url(r'^player/name_lookup','mafiaStats.views.nameLookup',name='mafiastats_name_lookup'),
	url(r'^game/(?P<game_id>\d+)/edit$','mafiaStats.views.edit',name='mafiastats_edit'),
	url(r'^link/?','mafiaStats.views.link',name='mafiastats_link'),
	url(r'^unlink/(?P<pk>\d+)/?$','mafiaStats.views.unlink',name='mafiastats_unlink'),
	url(r'^team/(?P<team_id>\d+)/graph/$', 'mafiaStats.views.teamGraph',name='mafiastats_team_graph'),
	)
