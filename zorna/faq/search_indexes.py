import datetime
from haystack.indexes import *
from haystack import site
from zorna.faq.models import FaqQuestion


class FaqQuestionIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    faq_name = CharField()
    faq = CharField()    
    category = CharField()    

    def get_model(self):
        return FaqQuestion

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(time_updated__lte=datetime.datetime.now())

    def prepare(self, obj):
        self.prepared_data = super(FaqQuestionIndex, self).prepare(obj)
        category = obj.category
        faq = category.faq
        self.prepared_data['faq_name'] = faq.name
        self.prepared_data['faq'] = str(faq.pk)
        self.prepared_data['category'] = category.name
        return self.prepared_data   
    
site.register(FaqQuestion, FaqQuestionIndex)