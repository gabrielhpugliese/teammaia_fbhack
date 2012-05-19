from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^login/', 'django_fukinbook.views.login', name='login'),
    url(r'^canvas/', 'facecards.views.canvas', name='canvas'),
    url(r'^keep_alive/', 'facecards.views.keep_alive', name='keep_alive'),
    url(r'^game_request/', 'facecards.views.game_request', name='game_request'),
    url(r'^refresh_games/', 'facecards.views.refresh_games', name='refresh_games'),
    url(r'^play/(?P<game_pk>\d+)', 'facecards.views.play', name='play'),
    
    
    url(r'^admin/', include(admin.site.urls)),
)
