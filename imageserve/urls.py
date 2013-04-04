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
    url(r'^wit_for_page$', views.wit_for_page),
    url(r'^page_for_wit$', views.page_for_wit),
    url(r'^id_for_wit$', views.id_for_wit),
    url(r'^set_page/(?P<first_last>first|last)$', views.set_page),
    url(r'^save_pages$', views.save_pages),
    url(r'^title_author$', views.title_author)
)