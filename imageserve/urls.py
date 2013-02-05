from django.conf.urls import patterns, include, url
from imageserve import views
import divaserve
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^/?$', views.main),
    url(r'^codex/(?P<ms_id>[a-zA-Z0-9_-]+)$', views.manuscript),
    url(r'^metadata/?', views.metadata),
    url(r'^divaserve/?', views.diva),
    url(r'^login/?', 'django.contrib.auth.views.login', {'template_name': 'templates/login.html'}),
    url(r'^logout/?', views.logout_view),
)