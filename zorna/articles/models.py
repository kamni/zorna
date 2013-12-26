import os
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_noop
from django.core.files.storage import FileSystemStorage
from django.template.defaultfilters import slugify

from zorna.models import ZornaEntity
from zorna.utilit import get_upload_articles_images, get_upload_articles_files
from zorna.articles.managers import ArticleCategoryManager

from mptt.models import MPTTModel

ARTICLES_NOTIFICATIONS = (
    (0, _(u'No email notification')),
    (1, _(u'Send email notification')),
    (2, _(u'Let the author decide')),
)


# cache category slug( id:slug )
categories_slugs = {}


class ArticleCategory(MPTTModel, ZornaEntity):
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children')
    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255, null=True, blank=True)
    template = models.TextField(_('Template'), blank=True)
    allow_comments = models.BooleanField(_(u'Allow comment'))
    email_notification = models.IntegerField(max_length=1, choices=ARTICLES_NOTIFICATIONS, default=0, help_text=_(
        u'Users will receive email notification when an article is published or updated'))
    objects = ArticleCategoryManager()

    class Meta:
        verbose_name = _('articles category')
        verbose_name_plural = _('articles categories')
        ordering = ['tree_id', 'lft']
        db_table = settings.TABLE_PREFIX + "articles_categories"

    def __unicode__(self):
        return self.name

    def get_complete_slug(self):
        if self.pk and categories_slugs.has_key(self.pk):
            return categories_slugs[self.pk]

        url = u''
        for ancestor in self.get_ancestors(ascending=True):
            url = ancestor.slug + u'/' + url
        categories_slugs[self.pk] = url
        return url

    def get_url_path(self):
        url = self.get_complete_slug() + self.slug
        return reverse('category-by-path', args=[url])

    def get_acl_permissions():
        return {
            'reader': ugettext_noop(u'Who can browse this category'),
            'writer': ugettext_noop(u'Who can submit articles to this category'),
            'manager': ugettext_noop(u'Who can manage this category'),
        }
    get_acl_permissions = staticmethod(get_acl_permissions)

ARTICLE_STATES = (
    (0, 'Draft'),
    (1, 'Published'),
    (2, 'Archived'),
)

article_image_storage = FileSystemStorage(
    location=get_upload_articles_images(), base_url='/images/articles/')


def get_image_filepath_storage(instance, filename):
    s = os.path.splitext(filename)
    filename = u"%s%s" % (slugify(s[0]), s[1])
    return os.path.join(u"%s/%s" % (str(instance.pk), filename))


class ArticleStory(ZornaEntity):
    categories = models.ManyToManyField(ArticleCategory, verbose_name=_(
        'categories'), blank=True, editable=False)
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255, null=True, blank=True)
    head = models.TextField(_('Head'), blank=True)
    body = models.TextField(_('Body'))
    state = models.IntegerField(
        max_length=1, choices=ARTICLE_STATES, default=0, editable=False)
    image = models.ImageField(
        upload_to=get_image_filepath_storage, storage=article_image_storage, blank=True)
    mimetype = models.CharField(max_length=64, editable=False)
    allow_comments = models.BooleanField(_(u'Allow comment'))

    class Meta:
        verbose_name = _('story')
        verbose_name_plural = _('stories')
        db_table = settings.TABLE_PREFIX + "stories"

    def get_absolute_url(self, category_id=None):
        if category_id is None:
            categories = self.categories.all()
            if categories:
                category_id = categories[0].pk
            else:
                return ''
        if category_id:
            return reverse('view_story', args=[category_id, self.pk, self.slug])
        else:
            return ''

    def __unicode__(self):
        return self.title

article_file_storage = FileSystemStorage(
    location=get_upload_articles_files(), base_url='/articles/file')


def get_file_filepath_storage(instance, filename):
    s = os.path.splitext(filename)
    filename = u"%s%s" % (slugify(s[0]), s[1])
    return os.path.join(u"%s/%s" % (str(instance.article_id), filename))


class ArticleAttachments(models.Model):
    attached_file = models.FileField(
        upload_to=get_file_filepath_storage, storage=article_file_storage)
    description = models.CharField(_('Description'), max_length=255)
    mimetype = models.CharField(max_length=255, editable=False)
    article = models.ForeignKey(ArticleStory, verbose_name=_(
        'article'), blank=True, editable=False)

    class Meta:
        verbose_name = _('article attachments')
        verbose_name_plural = _('article attachments')
        db_table = settings.TABLE_PREFIX + "articles_attachments"


class ArticleComments(ZornaEntity):
    title = models.CharField(_('Title'), max_length=255, blank=True)
    comment = models.TextField(_('Comment'))
    article = models.ForeignKey(ArticleStory, verbose_name=_(
        'article'), blank=True, editable=False)

    class Meta:
        verbose_name = _('article comment')
        verbose_name_plural = _('article comments')
        db_table = settings.TABLE_PREFIX + "articles_comments"
