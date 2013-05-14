from django.conf.urls.defaults import url, patterns

from zorna.acl import views


urlpatterns = patterns('',
                       url(r'^groups/(?P<ct>\d+)/(?P<object>\d+)/$',
                           views.acl_groups_object,
                           name='acl_groups_object'),
                       url(r'^users/(?P<ct>\d+)/(?P<object>\d+)/$',
                           views.acl_users_object,
                           name='acl_users_object'),
                       )
