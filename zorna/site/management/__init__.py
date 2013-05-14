from django.db.models.signals import post_syncdb
import zorna.site.models
from zorna.site.models import SiteOptions, SITES_OPTIONS, handler_views_was_called

def siteoptions_post_save(sender, **kwargs):
	handler_views_was_called()


post_syncdb.connect(siteoptions_post_save, sender=zorna.site.models)