import os
import sys
 
path = '/var/www/'
if path not in sys.path:
    sys.path.append(path)
 
sys.path.append('/var/www/zornasite/')
 
os.environ['DJANGO_SETTINGS_MODULE'] = 'zornasite.settings'
 
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
