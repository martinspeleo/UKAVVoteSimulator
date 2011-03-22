from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
     (r'^form/([^/]*)/([^/]*)/$', "avsimulation.views.form"),
     (r'^fptpresults/$', "avsimulation.views.run_election"),
     (r'^$', "avsimulation.views.frontpage"),

    # Uncomment the admin/doc line below to enable admin documentation:
     (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/', include(admin.site.urls)),
)
