import os
from django.conf import settings
from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url
from zorna.utils import zorna_category, zorna_stories_archives
from zorna.admin import site

urlpatterns += patterns('',
    (r'^admin/', include(site.urls)),
    (r'^ckeditor/', include('ckeditor.urls')),
    (r'^account/', include('zorna.account.urls')),
    (r'^acl/', include('zorna.acl.urls')),
    (r'^articles/', include('zorna.articles.urls')),
    (r'^communities/', include('zorna.communities.urls')),
    (r'^calendars/', include('zorna.calendars.urls')),
    (r'^faq/', include('zorna.faq.urls')),
    (r'^site/', include('zorna.site.urls')),
    (r'^notes/', include('zorna.notes.urls')),
    (r'^fileman/', include('zorna.fileman.urls')),
    (r'^forms/', include('zorna.forms.urls')),
    (r'^pages/', include('zorna.pages.urls')),
    (r'^menus/', include('zorna.menus.urls')),
    (r'^search/', include('zorna.search.urls')),
    )

try:
    plugins_path = os.path.join(settings.PROJECT_PATH, 'zorna_plugins')
    for app in os.listdir(plugins_path):
        app_path = os.path.join(plugins_path, app)
        if 'zorna_plugins.%s' % app in settings.INSTALLED_APPS and os.path.isdir(app_path):
            urlpatterns += patterns('',
                (r'^plugin/%s/' % app, include('zorna_plugins.%s.urls' % app)),
                )
except:
    pass

urlpatterns += patterns('',
    url(r'^su/(?P<username>.*)/$', 'zorna.utils.su', {'redirect_url': '/'}),
    url(r'^content/(?P<path>.*)$', 'zorna.utils.view_content', name='zorna_content'),
    url(r'^(?P<path>.*)/(?P<year>\d{4})/(?P<month>\d{2})/$', zorna_stories_archives, name='zorna_stories_archives'),
    url(r'^(?P<path>.*)$', zorna_category, name='category-by-path'),
    )
