import os

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

ZORNA_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(PROJECT_PATH, 'zorna_search_index')

ZORNA_SKIN = "default"
ZORNA_CONTENT = "html/%s" % ZORNA_SKIN


try:
    execfile(os.path.join(PROJECT_PATH, 'zorna/zorna_settings.py'))
except ImportError:
    pass

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'zornasite',  # Or path to database file if using sqlite3.
        'USER': '',  # Not used with sqlite3.
        'PASSWORD': '',  # Not used with sqlite3.
        'HOST': '',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',  # Set to empty string for default. Not used with sqlite3.
    }
}

TABLE_PREFIX = 'zorna_'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr_FR'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'qsdkhwxy3hqsnd!wxch#hwncn)xcd2qlnk:*;lwxcnwxc09xc!'

MIDDLEWARE_CLASSES += (
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'zorna.debug_middleware.DebugFooter',
    # 'snippetscream.ProfileMiddleware',
)

ROOT_URLCONF = 'zornasite.urls'

INSTALLED_APPS += (
)

# ACTSTREAM_ACTION_MODELS = ('auth.user', 'team.teamproject', 'team.teamprojecttask', 'team.teamprojecttaskconversation', 'team.teamprojectpage')

INTERNAL_IPS = ('127.0.0.1',)

ZORNA_UPLOAD_PATH = os.path.join(PROJECT_PATH, 'upload')

LOGIN_REDIRECT_URL = '/'

EMAIL_HOST = ''
DEFAULT_FROM_EMAIL = ''
ACCOUNT_ACTIVATION_DAYS = 4
CACHE_BACKEND = 'locmem://'
REDIRECT_FIELD_NAME = 'next'
ZORNA_MAIL_MAXPERPACKET = 99

RECAPTCHA_PUBKEY = '6LfYDsMSAAAAAO4Afh_Z_7G0jD9XrFw99dMCHnbh'
RECAPTCHA_PRIVKEY = '6LfYDsMSAAAAABhBgJp1lZJJCdwnrt9UM2Ff6zf2'

EMBEDLY_KEY = 'fc0b22b6f41111e0a3514040d3dc5c07'

STATIC_URL = '/zckeditor/'
CKEDITOR_MEDIA_PREFIX = '/zckeditor/ckeditor/'
CKEDITOR_UPLOAD_PATH = os.path.join(ZORNA_UPLOAD_PATH, 'ickeditor')
CKEDITOR_UPLOAD_PREFIX = '/images/ckeditor'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': "Full",
        'width': 740,
        'height': 300,
        'toolbarCanCollapse': False
	# 'extraPlugins': 'stylesheetparser',
        # 'contentsCss': ['/zmedia/css/articles.css']
    },
    'forms_config': {
        'toolbar': "Basic",
        'width': 740,
        'height': 150,
        'toolbarCanCollapse': False
        # 'contentsCss': ['/zmedia/css/articles.css']
    },
}
