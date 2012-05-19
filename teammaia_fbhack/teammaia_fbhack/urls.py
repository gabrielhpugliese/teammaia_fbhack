from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^login/', 'django_fukinbook.views.login', name='login'),
    url(r'^canvas/', 'facecards.views.canvas', name='canvas'),
    url(r'^keep_alive/', 'facecards.views.keep_alive', name='keep_alive'),
    url(r'^game_request/', 'facecards.views.game_request', name='game_request'),
    url(r'^refresh_logged_friends/', 'facecards.views.ajax_update_logged_friends', name='ajax_update_logged_friends'),
    url(r'^refresh_games/', 'facecards.views.refresh_games', name='refresh_games'),
    url(r'^refresh_my_challenge/', 'facecards.views.refresh_my_challenge', 
        name='refresh_my_challenge'),
    url(r'^play/(?P<game_pk>\d+)', 'facecards.views.play', name='play'),
    url(r'^finish_game/', 'facecards.views.finish_game', name='finish_game'),
    url(r'^check_finish/(?P<game_pk>\d+)', 'facecards.views.check_finish', 
        name='check_finish'),
    url(r'^get_next_card/', 'facecards.views.get_next_card', 
        name='get_next_card'),
    url(r'^get_turn/(?P<game_pk>\d+)', 'facecards.views.get_turn', name='get_turn'),
    url(r'^get_lock/', 'facecards.views.get_lock', name='get_lock'),
    url(r'^resolve_round/', 'facecards.views.resolve_round', name='resolve_round'),
    
    url(r'^admin/', include(admin.site.urls)),
)
