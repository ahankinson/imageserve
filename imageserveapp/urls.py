from django.conf.urls import patterns, url
from imageserveapp import views
import divaserve


urlpatterns = patterns('',
    url(r'^/?$', views.main, name='main'),
    url(r'witness/(?P<ms_id>[a-zA-Z0-9_-]+)$', views.manuscript, name='manuscript'),
    url(r'canvas/?', views.canvas, name='canvas'),
    url(r'divaserve/?', views.diva, name='diva'),
)