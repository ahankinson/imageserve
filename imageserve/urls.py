from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^', include('imageserveapp.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^settings/', include('dbsettings.urls')),
)
