from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from mptt.models import MPTTModel


class ZornaMenuItem(MPTTModel):
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children')
    name = models.CharField(_(u'name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    url = models.CharField(_(
        u'url'), max_length=255, blank=True, editable=False)
    target_blank = models.BooleanField(_(u'Open in new window'))
    content_type = models.ForeignKey(
        ContentType, null=True, blank=True, editable=False)
    object_id = models.IntegerField(editable=False, null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    extra_info = models.CharField(_(
        'extra'), max_length=255, editable=False, default='')

    class Meta:
        verbose_name = _('menu item')
        verbose_name_plural = _('menu items')
        ordering = ['tree_id', 'lft']
        db_table = settings.TABLE_PREFIX + "menu_items"

    def __unicode__(self):
        return u"%s" % self.name
