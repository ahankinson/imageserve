from django.conf.urls import patterns, include, url
from imageserve import views
import divaserve
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^/?$', views.main, name='main'),
    url(r'^codex/(?P<ms_id>[a-zA-Z0-9_-]+)$', views.manuscript, name='manuscript'),
    url(r'metadata/?', views.metadata, name='metadata'),
    url(r'divaserve/?', views.diva, name='diva'),
)