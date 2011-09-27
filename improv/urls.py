from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    ################
    ## Admin site ##
    ################
    (r'^admin/', include(admin.site.urls)),
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    #######################
    ## Pluggable outputs ##
    #######################
    (r'^output/simpletable/', include('simpletable.urls')),
)