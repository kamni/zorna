from django import template
from django.utils import simplejson

from tagging.models import Tag

from zorna.notes.models import ZornaNote

register = template.Library()


def auto_completion_search_tags_zornanote(context, input_suggest, input_result):
    """
    Render an auto completion to search users.
    """
    input_suggest = input_suggest
    input_result = input_result
    tags = Tag.objects.usage_for_model(ZornaNote)
    data = [(x.name, x.name) for x in tags]
    tags_data = simplejson.dumps(data)
    return locals()

auto_completion_search_tags_zornanote = register.inclusion_tag(
    'notes/ac_search_tags.html',
    takes_context=True
)(auto_completion_search_tags_zornanote)
