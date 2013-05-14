from django.conf.urls.defaults import url, patterns

from zorna.search.views import search


urlpatterns = patterns('',
    url(r'^$', search, name='haystack_search'),
                       )
