from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^Mafiastats/', include('mafiastats.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/(.*)', admin.site.root),
     (r'^$', 'Mafiastats.mafiaStats.views.index'),
     (r'^site/(?P<site_id>\d+)/$', 'Mafiastats.mafiaStats.views.site'),
     (r'^site/(?P<site_id>\d+)/scoreboard/(?P<page>\d*)/{0,1}$','Mafiastats.mafiaStats.views.scoreboard'),
     (r'^site/(?P<site_id>\d+)/games/(?P<page>\d*)/{0,1}$','Mafiastats.mafiaStats.views.games'),
     (r'^site/(?P<site_id>\d+)/moderators/(?P<page>\d*)/{0,1}$','Mafiastats.mafiaStats.views.moderators'),
     (r'^game/add/(?P<site_id>\d*)/*$','Mafiastats.mafiaStats.views.add'),
     (r'^game/(?P<game_id>\d+)/$','Mafiastats.mafiaStats.views.game'),
     (r'^player/(?P<player_id>\d+)/$','Mafiastats.mafiaStats.views.player'),
     (r'^player/(?P<player_id>\d+)/played/$','Mafiastats.mafiaStats.views.playerPlayed'),
     (r'^player/(?P<player_id>\d+)/moderated/$','Mafiastats.mafiaStats.views.playerModerated'),
     (r'^player/name_lookup','Mafiastats.mafiaStats.views.nameLookup'),
     (r'^login/','django.contrib.auth.views.login',{'template_name':'login.html',}),
     (r'^logout/','django.contrib.auth.views.logout',{'template_name':'logout.htl','next_page':'/'}),
     (r'^register/','Mafiastats.mafiaStats.views.register'),
     (r'^account/profile','Mafiastats.auth.views.profile'),
     url(r'^account/register/$', 'django_authopenid.views.register', {'send_email':False},name='user_register'),
     url(r'^account/associate/complete/$', 'django_authopenid.views.complete_associate', {'send_email':False},name='user_complete_associate'),
     (r'^account/',include('django_authopenid.urls')),
    # (r'^openid/$','django_openidconsumer.views.begin'),
    # (r'^openid/complete/$', 'django_openidconsumer.views.complete'),
    # (r'^openid/signout/$', 'django_openidconsumer.views.signout'),

     #(r'^register/','Mafiastats.mafiaStats.views.register'),
)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

