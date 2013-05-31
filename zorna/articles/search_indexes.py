import datetime
from haystack.indexes import *
from haystack import site
from zorna.articles.models import ArticleStory


class ArticleStoryIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    author = CharField(model_attr='owner')
    pub_date = DateTimeField(model_attr='time_created')
    categories = MultiValueField()

    def get_model(self):
        return ArticleStory

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(time_updated__lte=datetime.datetime.now())

    def prepare_author(self, obj):
        return obj.owner.get_full_name()

    def prepare_categories(self, obj):
        # Since we're using a M2M relationship with a complex lookup,
        # we can prepare the list here.
        return [category.pk for category in obj.categories.all()]

site.register(ArticleStory, ArticleStoryIndex)
