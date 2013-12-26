import os
from django.conf import settings
from django.template import TemplateSyntaxError
from django import template
from django.contrib.auth.models import User
from django.utils import simplejson
from django.template import Variable

from zorna.forms.models import FormsForm, FormsFormEntry
from zorna.forms.api import forms_get_entry
from zorna.utilit import resize_image

register = template.Library()

@register.filter
def thumbnail(file, size='200w'):
    filehead, filetail = os.path.split(file.name)
    miniature_url = filehead + '/' + resize_image(file.path, size)
    return miniature_url


def auto_completion_search_users(context, input_suggest, input_result):
    """
    Render an auto completion to search users.

    Override ``account/ac_search_users.html`` if you want to change the
    design.
    """
    input_suggest = input_suggest
    input_result = input_result
    objects = User.objects.all()
    data = [("%s %s" % (x.last_name, x.first_name), x.id) for x in objects]
    json_data = simplejson.dumps(data)
    return locals()

auto_completion_search_users = register.inclusion_tag(
    'account/ac_search_users.html',
    takes_context=True
)(auto_completion_search_users)


def json_list_users(context):
    """
    """
    objects = User.objects.all()
    users_list = [("%s %s" % (x.last_name, x.first_name), x.id)
                  for x in objects]
    json_data = simplejson.dumps(users_list)
    return locals()

json_list_users = register.inclusion_tag(
    'account/ac_json_users.html',
    takes_context=True
)(json_list_users)


class get_user_profile_node(template.Node):

    def __init__(self, user_varname, columns_varname, rows_varname):
        self.columns_varname = columns_varname
        self.rows_varname = rows_varname
        self.user_varname = Variable(user_varname)

    def render(self, context):
        try:
            form = FormsForm.objects.get(slug=settings.ZORNA_USER_PROFILE_FORM)
            try:
                entry = form.entries.get(
                    account__id=self.user_varname.resolve(context))
            except FormsFormEntry.DoesNotExist:
                entry = None
        except Exception as e:
            entry = None
        if entry:
            context[self.columns_varname], context[
                self.rows_varname] = forms_get_entry(entry)
        else:
            context[self.columns_varname] = None
            context[self.rows_varname] = None
        return ''


@register.tag(name="get_user_profile")
def get_user_profile(parser, token):
    bits = token.split_contents()
    if 5 != len(bits):
        raise TemplateSyntaxError('%r expects 4 arguments' % bits[0])
    if bits[-3] != 'as':
        raise TemplateSyntaxError(
            '%r expects "as" as the third argument' % bits[0])
    columns_varname = bits[-2]
    rows_varname = bits[-1]
    user_varname = bits[-4]
    return get_user_profile_node(user_varname, columns_varname, rows_varname)
