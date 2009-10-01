from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from registration import views as reg_views
admin.autodiscover()
from Mafiastats.mafiaStats import urls as statUrls

urlpatterns = patterns('',
    # Example:
    # (r'^Mafiastats/', include('mafiastats.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/(.*)', admin.site.root),
     url(r'^$', 'Mafiastats.mafiaStats.views.index',name='index'),
     (r'^stat/',include('Mafiastats.mafiaStats.urls')),
     url(r'^account/profile/?$','Mafiastats.mafiaStats.views.profile',name='account_profile'),
     url(r'^account/profile/(?P<pk>\d*)/?$','Mafiastats.mafiaStats.views.profile',name='account_profile'),
     url(r'^account/register/$', 'django_authopenid.views.register', {'send_email':False},name='user_register'),
     url(r'^account/signup/$',reg_views.register,name='registration_register'),
     url(r'^account/associate/complete/$', 'django_authopenid.views.complete_associate', {'send_email':False},name='user_complete_associate'),
     (r'^account/',include('django_authopenid.urls')),
     (r'^comments/',include('django.contrib.comments.urls')),
    # (r'^openid/$','django_openidconsumer.views.begin'),
    # (r'^openid/complete/$', 'django_openidconsumer.views.complete'),
    # (r'^openid/signout/$', 'django_openidconsumer.views.signout'),

     #(r'^register/','Mafiastats.mafiaStats.views.register'),
)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

