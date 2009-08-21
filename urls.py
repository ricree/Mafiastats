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
     (r'^$', 'Mafiastats.mafiaStat.views.index'),
     (r'^site/(?P<site_id>\d+)/(?P<page>\d*)/{0,1}$', 'Mafiastats.mafiaStat.views.site'),
     (r'^site/(?P<site_id>\d+)/scoreboard/(?P<page>\d*)/{0,1}$','Mafiastats.mafiaStat.views.scoreboard'),
     (r'^site/(?P<site_id>\d+)/games/(?P<page>\d*)/{0,1}$','Mafiastats.mafiaStat.views.games'),
     (r'^site/(?P<site_id>\d+)/moderators/(?P<page>\d*)/{0,1}$','Mafiastats.mafiaStat.views.moderators'),
     (r'^game/add/(?P<site_id>\d*)/*$','Mafiastats.mafiaStat.views.add'),
     (r'^game/(?P<game_id>\d+)/$','Mafiastats.mafiaStat.views.game'),
     (r'^player/(?P<player_id>\d+)/$','Mafiastats.mafiaStat.views.player'),
     (r'^player/(?P<player_id>\d+)/played/$','Mafiastats.mafiaStat.views.playerPlayed'),
     (r'^player/(?P<player_id>\d+)/moderated/$','Mafiastats.mafiaStat.views.playerModerated'),
     (r'^player/name_lookup','Mafiastats.mafiaStat.views.nameLookup'),
     (r'^login/','django.contrib.auth.views.login',{'template_name':'login.html',}),
     (r'^logout/','django.contrib.auth.views.logout',{'template_name':'logout.htl','next_page':'/'}),
     (r'^register/','Mafiastats.mafiaStat.views.register'),
     (r'^account/profile/','mafiastats.auth.views.profile'),
     (r'^account/',include('django_authopenid.urls')),
    # (r'^openid/$','django_openidconsumer.views.begin'),
    # (r'^openid/complete/$', 'django_openidconsumer.views.complete'),
    # (r'^openid/signout/$', 'django_openidconsumer.views.signout'),

     #(r'^register/','Mafiastats.mafiaStat.views.register'),
)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

