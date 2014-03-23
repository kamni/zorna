import os

ACTSTREAM_SETTINGS = {
    'MODELS': ('auth.user',),
}
plugins_path = os.path.join(PROJECT_PATH, 'zorna_plugins')
if os.path.isdir(plugins_path):
    for app in os.listdir(plugins_path):
        app_path = os.path.join(plugins_path, app)
        if os.path.isdir(app_path):
            try:
                execfile(os.path.join(app_path, 'settings.py'))
            except:
                pass

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'skins/' + ZORNA_SKIN),
    os.path.join(PROJECT_PATH, 'skins/%s/templates' % ZORNA_SKIN),
    os.path.join(PROJECT_PATH, 'skins/templates'),
    os.path.join(PROJECT_PATH, 'zorna/templates/skins/default'),
    os.path.join(PROJECT_PATH, 'zorna_plugins'),
)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'zorna/media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/zmedia/'
MEDIA_PLUGIN_URL = '/pmedia/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.comw/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    "django.core.context_processors.i18n",
    "django.core.context_processors.static",
    "zorna.context_processors.alerts",
    "zorna.context_processors.zsettings",
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'zorna.account.middleware.ActivityMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.humanize',
    'mptt',
    'haystack',
    'actstream',
    'zorna',
    'zorna.pages',
    'zorna.calendars',
    'zorna.articles',
    'zorna.communities',
    'zorna.account',
    'zorna.acl',
    'zorna.faq',
    'zorna.site',
    'zorna.notes',
    'zorna.fileman',
    'zorna.forms',
    'zorna.menus',
    'ckeditor',
    'south',
    'schedule',
    'tagging',
    'taggit',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Zorna
AUTH_PROFILE_MODULE = "account.UserProfile"
LOGIN_URL = '/account/login/'


HAYSTACK_SEARCH_ENGINE = ZORNA_SEARCH_ENGINE
HAYSTACK_SITECONF = 'zorna.search.search_sites'
