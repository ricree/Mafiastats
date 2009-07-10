from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^mafiastats/', include('mafiastats.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/(.*)', admin.site.root),
     (r'^$', 'mafiastats.mafiaStats.views.index'),
     (r'^site/(?P<site_id>\d+)/$', 'mafiastats.mafiaStats.views.site'),
     (r'^site/(?P<site_id>\d+)/scoreboard/$','mafiastats.mafiaStats.views.scoreboard'),
     (r'^site/(?P<site_id>\d+)/games/$','mafiastats.mafiaStats.views.games'),
     (r'^game/add/$','mafiastats.mafiaStats.views.add'),
     (r'^game/(?P<game_id>\d+)/$','mafiastats.mafiaStats.views.game'),
     (r'^player/(?P<player_id>\d+)/$','mafiastats.mafiaStats.views.player'),
     (r'^player/(?P<player_id>\d+)/played/$','mafiastats.mafiaStats.views.playerPlayed'),
     (r'^player/(?P<player_id>\d+)/moderated/$','mafiastats.mafiaStats.views.playerModerated'),
)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

