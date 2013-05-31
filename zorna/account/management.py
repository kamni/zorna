from django.db.models.signals import post_syncdb
from django.utils.translation import ugettext_noop
from zorna.account import models as account_model
from zorna.account.models import UserGroup


def zorna_post_syncdb(app, created_models, verbosity, **kwargs):
    if UserGroup.objects.count() > 0:
        return
    p = UserGroup(name=ugettext_noop(u"Public"), parent=None)
    p.save()
    UserGroup(name=ugettext_noop(u"Anonymous"), parent=p).save()
    UserGroup(name=ugettext_noop(u"Registered"), parent=p).save()

post_syncdb.connect(zorna_post_syncdb, sender=account_model)
