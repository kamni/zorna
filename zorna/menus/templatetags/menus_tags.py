
from django.template import TemplateSyntaxError
from django import template
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from zorna.menus.models import ZornaMenuItem

from zorna.acl.models import get_allowed_objects
from zorna.articles.models import ArticleCategory
from zorna.forms.models import FormsForm
from zorna.faq.models import Faq

register = template.Library()


def get_menu_children(request, menu):
    ao_articles = get_allowed_objects(request.user, ArticleCategory, 'reader')
    ao_faqs = get_allowed_objects(request.user, Faq, 'reader')
    ao_forms_sub = get_allowed_objects(request.user, FormsForm, 'creator')
    ao_forms_list = get_allowed_objects(request.user, FormsForm, 'viewer')
    ct_articles = ContentType.objects.get(model='articlecategory')
    ct_faqs = ContentType.objects.get(model='faq')
    ct_forms = ContentType.objects.get(model='formsform')
    children = menu.get_children().filter(Q(object_id__in=ao_articles, content_type=ct_articles) |
                                          Q(object_id__in=ao_faqs, content_type=ct_faqs) |
                                          Q(object_id__in=ao_forms_sub, content_type=ct_forms) |
                                          Q(object_id__in=ao_forms_list, content_type=ct_forms) |
                                          Q(object_id__isnull=True))
    for child in children:
        if child.object_id and child.content_type == ct_articles:
            child.url = child.content_object.get_url_path()
        elif child.object_id and child.content_type == ct_faqs:
            child.url = child.content_object.get_url_path()
        elif child.object_id and child.content_type == ct_forms:
            if child.extra_info == 'submission':
                child.url = child.content_object.get_url_path()
            else:
                child.url = child.content_object.get_url_browse_path()
    return children


def show_menu(context, menu_name, menu_type=None):
    '''
    {% show_menu slug extra_info %}
    display menu and recurse over children
    '''
    menu = ZornaMenuItem.objects.get(slug=menu_name)
    if menu.object_id and menu.extra_info == 'browse':
        menu.url = menu.content_object.get_url_browse_path()
    elif menu.object_id:
        menu.url = menu.content_object.get_url_path()
    context['menu'] = menu
    context['menu_name'] = menu_name
    request = context['request']
    context['menu_children'] = get_menu_children(request, menu)
    if menu_type:
        context['menu_type'] = menu_type
    return context
register.inclusion_tag('menu.html', takes_context=True)(show_menu)


def show_menu_item(context, menu_item):
    '''
    {% show_menu menu %}
    Print <li>...</li>
    '''
    if not isinstance(menu_item, ZornaMenuItem):
        raise template.TemplateSyntaxError, 'Given argument must be a ZornaMenuItem object.'
    request = context['request']
    context['menu_item'] = menu_item
    context['menu_item_children'] = get_menu_children(request, menu_item)
    return context
register.inclusion_tag(
    'menu_item.html', takes_context=True)(show_menu_item)


@register.tag(name="menu_item")
def menu_item(parser, token):
    '''
    {% menu_item slug as menu %}
    return ZornaMenuItem menu item with menu.menu_children as children
    slug can be also a variable
    '''
    bits = token.split_contents()
    if 4 != len(bits):
        raise TemplateSyntaxError('%r expects 4 arguments' % bits[0])
    if bits[-2] != 'as':
        raise TemplateSyntaxError(
            '%r expects "as" as the second argument' % bits[0])
    menu_item = bits[1]
    varname = bits[-1]
    return menu_item_node(menu_item, varname)


class menu_item_node(template.Node):

    def __init__(self, menu_item, var_name):
        if not (menu_item[0] == menu_item[-1] and menu_item[0] in ('"', "'")):
            self.menu_item = template.Variable(menu_item)
        else:
            self.menu_item = menu_item[1:-1]
        self.var_name = var_name

    def render(self, context):
        request = context['request']
        try:
            menu_item = self.menu_item.resolve(context)
        except:
            menu_item = self.menu_item

        try:
            mi = ZornaMenuItem.objects.get(slug=menu_item)
        except ZornaMenuItem.DoesNotExist:
            return ''
        ao_articles = get_allowed_objects(
            request.user, ArticleCategory, 'reader')
        if mi.object_id and mi.content_type == ContentType.objects.get(model='ArticleCategory'):
            if not mi.object_id in ao_articles:
                return ''
        mi.menu_children = get_menu_children(request, mi)
        context[self.var_name] = mi
        return ''
