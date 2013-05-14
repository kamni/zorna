from django.db.models.signals import post_syncdb
from django.utils.translation import ugettext_noop
from zorna.menus import models as menus_model
from zorna.menus.models import ZornaMenuItem

def menus_post_syncdb(app, created_models, verbosity, **kwargs):
    if ZornaMenuItem.objects.count() > 0:
        return
    p = ZornaMenuItem(name='Top menu', slug='top-menu', parent=None)
    p.save()
    ZornaMenuItem(name='About', slug='about', url='/content/about/', parent=p).save()

post_syncdb.connect(menus_post_syncdb, sender=menus_model)
