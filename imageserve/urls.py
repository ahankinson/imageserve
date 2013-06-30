from django.conf.urls import patterns, include, url
from imageserve import views
import divaserve
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^/?$', views.main),
    url(r'^codex/(?P<ms_id>[a-zA-Z0-9_-]+)$', views.manuscript),
    url(r'^search/$', views.search),
    url(r'^goto/$', views.goto),
    url(r'^metadata/?', views.metadata),
    url(r'^divaserve/?', views.diva),
    url(r'^login/?', 'django.contrib.auth.views.login', {'template_name': 'templates/login.html'}),
    url(r'^logout/?', views.logout_view),
    url(r'^wit_for_page$', views.wit_for_page),
    url(r'^folio_for_page$', views.folio_for_page),
    url(r'^page_for_folio$', views.page_for_folio),
    url(r'^page_for_wit$', views.page_for_wit),
    url(r'^set_folio$', views.set_folio),
    url(r'^interpolate_after$', views.interpolate_after),
    url(r'^title_author$', views.title_author),
    url(r'^save_folios$', views.save_folios),
    url(r'^remove_folios$', views.remove_folios),
    url(r'^discard_changes$', views.discard_changes)
)
