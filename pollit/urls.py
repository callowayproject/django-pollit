from django.conf.urls.defaults import *

urlpatterns = patterns('pollit.views',
    url(r'^$',
        'index',
        name='pollit_index'),
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<slug>[\w-]+)/$',
        'detail',
        name='pollit_detail'),
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<slug>[\w-]+)/results/$',
        'results',
        name='pollit_results')
)
