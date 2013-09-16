from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

from imageserve.views.main import main
from imageserve.views.manuscript import manuscript
# from imageserve.views.search import search
# from imageserve.views.diva import diva

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^/?$', main),
    url(r'^codex/(?P<ms_id>[a-zA-Z0-9_-]+)$', manuscript),
    # url(r'^search/$', search),
    # url(r'^goto/$', views.goto),
    # url(r'^metadata/?', views.metadata),
    # url(r'^divaserve/?', diva),
    # url(r'^login/?', 'django.contrib.auth.views.login', {'template_name': 'templates/login.html'}),
    # url(r'^logout/?', views.logout_view),
    # url(r'^wit_for_page$', views.wit_for_page),
    # url(r'^folio_for_page$', views.folio_for_page),
    # url(r'^page_for_folio$', views.page_for_folio),
    # url(r'^page_for_wit$', views.page_for_wit),
    # url(r'^set_folio$', views.set_folio),
    # url(r'^interpolate_after$', views.interpolate_after),
    # url(r'^title_author$', views.title_author),
    # url(r'^save_folios$', views.save_folios),
    # url(r'^remove_folios$', views.remove_folios),
    # url(r'^discard_changes$', views.discard_changes)
)
