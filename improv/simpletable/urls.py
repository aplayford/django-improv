from django.conf.urls.defaults import *

urlpatterns = patterns('simpletable.views',
    url(r'^view/(?P<slug>[\w-]+)/', 'render_table', {}, name="simpletable_view"),
)