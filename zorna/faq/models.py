from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_noop
from django.core.urlresolvers import reverse

from zorna.models import ZornaEntity
from zorna.faq.managers import FaqQuestionManager
import defines


class Faq(ZornaEntity):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)

    class Meta:
        ordering = ['name']
        db_table = settings.TABLE_PREFIX + "faq"

    def __unicode__(self):
        return self.name  

    def get_acl_permissions():
        return { 
            u'reader': ugettext_noop(u'Who can browse this faq'),
            u'manager': ugettext_noop(u'Who can manage this faq'),
            }
    get_acl_permissions = staticmethod(get_acl_permissions)

    def get_url_path(self):
        url = self.slug
        return reverse('browse_faq', args=[url])    
    
class FaqCategory(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)
    sort_order = models.IntegerField(_('sort order'), default=0, help_text='The order you would like the topic to be displayed.')
    faq = models.ForeignKey(Faq)

    class Meta:
        ordering = ['sort_order', 'name']
        db_table = settings.TABLE_PREFIX + "faq_categories"

    def __unicode__(self):
        return self.name  

    def questions(self):
        return FaqQuestion.objects.filter(category=self.pk)

    def get_url_path(self):
        url = self.faq.slug+'/'+self.slug
        return reverse('browse_faq', args=[url])
    
    def get_active_questions(self):
        return FaqQuestion.objects.filter(status=defines.STATUS_ACTIVE, category=self.pk)
    
class FaqQuestion(ZornaEntity):
    """
    Represents a frequently asked question.
    """
    slug = models.SlugField( max_length=100, help_text="This is a unique identifier that allows your questions to display its detail view, ex 'how-can-i-contribute'", )
    category = models.ForeignKey(FaqCategory)
    question = models.TextField(_('question'), help_text='The actual question itself.')
    answer = models.TextField( _('answer'), help_text='The answer text.' )    
    status = models.IntegerField( choices=defines.QUESTION_STATUS_CHOICES, default=defines.STATUS_INACTIVE, help_text="Only questions with their status set to 'Active' will be displayed." )
    sort_order = models.IntegerField(_('sort order'), default=0, help_text='The order you would like the question to be displayed.')
    objects = FaqQuestionManager()
    
    class Meta:
        ordering = ['sort_order', 'time_updated', ]
        db_table = settings.TABLE_PREFIX + "faq_questions"
        

    def __unicode__(self):
        return self.question

    def save(self, *args, **kwargs):
        super(FaqQuestion, self).save(*args, **kwargs)

    def is_active(self):
        return self.status == defines.STATUS_ACTIVE
    
    def get_absolute_url(self):
        return self.category.get_url_path() +'#' + self.slug
    

