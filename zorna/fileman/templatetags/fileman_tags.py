from django.template import TemplateSyntaxError
from django import template
from django.utils import simplejson

from tagging.models import Tag

from zorna.fileman.api import recent_files, get_allowed_shared_folders
from zorna.fileman.models import ZornaFile
from zorna.fileman.api import get_folder_files

register = template.Library()


def auto_completion_search_tags_zornafile(context, input_suggest, input_result):
    """
    Render an auto completion to search users.
    """
    input_suggest = input_suggest
    input_result = input_result
    tags = Tag.objects.usage_for_model(ZornaFile)
    data = [(x.name, x.name) for x in tags]
    tags_data = simplejson.dumps(data)
    return locals()

auto_completion_search_tags_zornafile = register.inclusion_tag(
    'fileman/ac_search_tags.html',
    takes_context=True
)(auto_completion_search_tags_zornafile)


class get_recent_files_node(template.Node):

    def __init__(self, limit, var_name, what='all'):
        self.what = what
        self.limit = limit
        self.var_name = var_name

    def render(self, context):
        request = context['request']
        context[self.var_name] = recent_files(request, self.what, self.limit)
        return ''


def parse_tag(parser, token, what):
    bits = token.split_contents()
    if 4 != len(bits):
        raise TemplateSyntaxError('%r expects 4 arguments' % bits[0])
    if bits[-2] != 'as':
        raise TemplateSyntaxError(
            '%r expects "as" as the third argument' % bits[0])
    limit = bits[1]
    varname = bits[-1]
    return get_recent_files_node(limit, varname, what)


@register.tag(name="get_recent_files")
def get_recent_files(parser, token):
    """
    {% get_recent_files 10 as recent_files %}
    {% for f in recent_files %}
    <a href="{{f.file_path}}">{{f.pk}},{{f.file_name}}</a><br />
    {% endfor %}
    """
    return parse_tag(parser, token, 'all')


@register.tag(name="get_recent_communities_files")
def get_recent_communities_files(parser, token):
    """
    {% get_recent_communities_files 10 as recent_files %}
    {% for f in recent_files %}
    <a href="{{f.file_path}}">{{f.pk}},{{f.file_name}}</a><br />
    {% endfor %}
    """
    return parse_tag(parser, token, 'communities')


@register.tag(name="get_recent_shared_files")
def get_recent_shared_files(parser, token):
    """
    {% get_recent_communities_files 10 as recent_files %}
    {% for f in recent_files %}
    <a href="{{f.file_path}}">{{f.pk}},{{f.file_name}}</a><br />
    {% endfor %}
    """
    return parse_tag(parser, token, 'shared')


@register.tag(name="get_recent_personal_files")
def get_recent_personal_files(parser, token):
    """
    {% get_recent_communities_files 10 as recent_files %}
    {% for f in recent_files %}
    <a href="{{f.file_path}}">{{f.pk}},{{f.file_name}}</a><br />
    {% endfor %}
    """
    return parse_tag(parser, token, 'personal')


class get_shared_folder_files_node(template.Node):

    def __init__(self, folder_id, path, limit, varname):
        self.folder_id = int(folder_id)
        self.path = path
        self.limit = limit
        self.var_name = varname

    def render(self, context):
        request = context['request']
        aof = get_allowed_shared_folders(request.user, ['reader'])
        if self.folder_id in aof:
            context[self.var_name] = get_folder_files(
                'F%s/%s' % (self.folder_id, self.path), self.limit)
        else:
            context[self.var_name] = []
        return ''


@register.tag(name="get_shared_folder_files")
def get_shared_folder_files(parser, token):
    """
    {% get_shared_folder_files ID 'PATH' limit as files %}
    {% for f in files %}
    <a href="{{f.file_path}}">{{f.pk}},{{f.file_name}}</a><br />
    {% endfor %}
    """
    bits = token.split_contents()
    if 6 != len(bits):
        raise TemplateSyntaxError('%r expects 5 arguments' % bits[0])
    if bits[-2] != 'as':
        raise TemplateSyntaxError(
            '%r expects "as" as the 4 argument' % bits[0])
    folder_id = bits[1]
    path = bits[2][1:-1]
    limit = bits[3]
    varname = bits[-1]
    return get_shared_folder_files_node(folder_id, path, limit, varname)
