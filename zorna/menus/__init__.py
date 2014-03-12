import shutil
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver

from .models import ZornaMenuItem
from ..utilit import get_upload_menus

@receiver(post_delete, sender=ZornaMenuItem)
def _zornamenuitem_delete(sender, instance, **kwargs):
	print "delete instance menu= %s" % instance.pk
	try:
		shutil.rmtree(u"%s/m%s" % (get_upload_menus(), instance.pk))
	except Exception, e:
		print e
