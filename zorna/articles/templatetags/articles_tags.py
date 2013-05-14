import os

from django.core.urlresolvers import reverse
from django.template import TemplateSyntaxError
from django import template
from django.template import Variable


from zorna.acl.models import get_allowed_objects
from zorna.articles.models import ArticleCategory, ArticleStory
    
register = template.Library() 

class categories_by_permission_node( template.Node ):
    def __init__(self, permission, var_name):
        self.permission = permission
        self.var_name = var_name
        
    def render(self, context):
        request = context['request']
        allowed_objects = get_allowed_objects(request.user, ArticleCategory, self.permission)        
        context[self.var_name] = allowed_objects
        return ''
    
@register.tag(name="get_categories_by_permission")        
def get_categories_by_permission( parser, token ):
    bits = token.split_contents()
    if 4 != len(bits):
        raise TemplateSyntaxError('%r expects 4 arguments' % bits[0])
    if bits[-2] != 'as':
        raise TemplateSyntaxError(
            '%r expects "as" as the second argument' % bits[0])
    permission = bits[1]
    varname = bits[-1]
    return categories_by_permission_node(permission, varname)


class category_childs_node( template.Node ):
    def __init__(self, permission, object, var_name):
        self.object = Variable(object)
        self.var_name = var_name
        self.permission = permission
        
    def render(self, context):
        request = context['request']
        allowed_objects = get_allowed_objects(request.user, ArticleCategory, self.permission)        
        object = self.object.resolve(context)
        categories = object.get_children().filter(id__in=allowed_objects)
        for cat in categories:
            cat.url = cat.get_url_path()
        context[self.var_name] = categories
        return ''
    
@register.tag(name="category_childs")        
def category_childs( parser, token ):
    bits = token.split_contents()
    if 5 != len(bits):
        raise TemplateSyntaxError('%r expects 5 arguments' % bits[0])
    if bits[-2] != 'as':
        raise TemplateSyntaxError(
            '%r expects "as" as the second argument' % bits[0])
    permission = bits[1]
    category = bits[2]
    varname = bits[-1]
    return category_childs_node(permission, category, varname)

class category_ancestors_node( template.Node ):
    def __init__(self, object, var_name):
        self.object = Variable(object)
        self.var_name = var_name
        
    def render(self, context):
        object = self.object.resolve(context)
        request = context['request']
        allowed_objects = get_allowed_objects(request.user, ArticleCategory, 'reader')        
        context[self.var_name] = object.get_ancestors().filter(id__in=allowed_objects)
        return ''


@register.tag(name="category_ancestors")        
def category_ancestors( parser, token ):
    bits = token.split_contents()
    if 4 != len(bits):
        raise TemplateSyntaxError('%r expects 4 arguments' % bits[0])
    if bits[-2] != 'as':
        raise TemplateSyntaxError(
            '%r expects "as" as the second argument' % bits[0])
    category = bits[1]
    varname = bits[-1]
    return category_ancestors_node(category, varname)

class category_roots_node( template.Node ):
    def __init__(self, permission, var_name):
        self.var_name = var_name
        self.permission = permission
        
    def render(self, context):
        request = context['request']
        allowed_objects = get_allowed_objects(request.user, ArticleCategory, self.permission)        
        categories = ArticleCategory.objects.filter(parent__isnull=True, id__in=allowed_objects)
        for cat in categories:
            cat.url = cat.get_url_path()
        context[self.var_name] = categories
        return ''


@register.tag(name="category_roots")        
def category_roots( parser, token ):
    bits = token.split_contents()
    if 4 != len(bits):
        raise TemplateSyntaxError('%r expects 4 arguments' % bits[0])
    if bits[-2] != 'as':
        raise TemplateSyntaxError(
            '%r expects "as" as the second argument' % bits[0])
    permission = bits[1]
    varname = bits[-1]
    return category_roots_node(permission, varname)

class get_recent_stories_node( template.Node ):
    def __init__(self, limit, var_name):
        self.limit = limit
        self.var_name = var_name
        
    def render(self, context):
        request = context['request']
        allowed_objects = get_allowed_objects(request.user, ArticleCategory, 'reader')        
        stories = ArticleStory.objects.select_related().filter(categories__in=allowed_objects).distinct().order_by('-time_updated')[:int(self.limit)]
        for story in stories:
            story.current_categories = story.categories.all()
            story.current_category = story.current_categories[0]
        context[self.var_name] = stories
        return ''


@register.tag(name="get_recent_stories")        
def get_recent_stories( parser, token ):
    bits = token.split_contents()
    if 4 != len(bits):
        raise TemplateSyntaxError('%r expects 4 arguments' % bits[0])
    if bits[-2] != 'as':
        raise TemplateSyntaxError(
            '%r expects "as" as the third argument' % bits[0])
    limit = bits[1]
    varname = bits[-1]
    return get_recent_stories_node(limit, varname)

class get_story_attachments_node( template.Node ):
    def __init__(self, story, var_name):
        self.story = Variable(story)
        self.var_name = var_name
        
    def render(self, context):
        request = context['request']
        s = self.story.resolve(context)
        allowed_objects = get_allowed_objects(request.user, ArticleCategory, 'reader')
        stories = ArticleStory.objects.filter(categories__in=allowed_objects, pk=s.pk)
        attachments = s.articleattachments_set.all()
        for f in attachments:
            f.file_name = os.path.basename(f.attached_file.name)
            f.file_url = reverse('get_story_file', args=[f.pk])
        if stories:
            context[self.var_name] = attachments
        else:       
            context[self.var_name] = None
        return ''


@register.tag(name="get_story_attachments")        
def get_story_attachments( parser, token ):
    bits = token.split_contents()
    if 4 != len(bits):
        raise TemplateSyntaxError('%r expects 4 arguments' % bits[0])
    if bits[-2] != 'as':
        raise TemplateSyntaxError(
            '%r expects "as" as the second argument' % bits[0])
    story = bits[1]
    varname = bits[-1]
    return get_story_attachments_node(story, varname)

def pages_item_menu(context, category, permission, template='pages_item_menu.html'):
    request = context['request']
    allowed_objects = get_allowed_objects(request.user, ArticleCategory, permission)        
    children = category.get_children().filter(id__in=allowed_objects)
    for cat in children:
        cat.url = cat.get_url_path()
    return {'template': template, 'children': children, 'category': category, 'request': request}

pages_item_menu = register.inclusion_tag(
    'extends.html',
    takes_context=True
)(pages_item_menu)