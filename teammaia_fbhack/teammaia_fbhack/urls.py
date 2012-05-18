from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^login/', 'django_fukinbook.views.login', name='login'),
    url(r'^canvas/', 'facecards.views.canvas', name='canvas'),
    url(r'^keepalive/', 'facecards.views.keepalive', name='keepalive'),
    
    
    url(r'^admin/', include(admin.site.urls)),
)
