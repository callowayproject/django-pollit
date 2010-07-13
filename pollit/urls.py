from django.conf.urls.defaults import *
from models import Poll

comment_info_dict = {
    'queryset': Poll.objects.filter(status__lt=3, comment_status__gt=1),
    'template_object_name': 'poll',
    'date_field': 'pub_date',
    'template_name': 'pollit/comments.html'
}

urlpatterns = patterns('',
    url(r'^$',
        'pollit.views.index',
        name='pollit_index'),
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<slug>[\w-]+)/$',
        'pollit.views.detail',
        name='pollit_detail'),
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<slug>[\w-]+)/results/$',
        'pollit.views.results',
        name='pollit_results'),
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{1,2})/(?P<slug>[\w-]+)/comments/$',
        'django.views.generic.date_based.object_detail',
        kwargs=comment_info_dict,
        name='pollit_comments')
)
