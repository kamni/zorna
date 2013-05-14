
from django.template import TemplateSyntaxError
from django import template
from django.contrib.contenttypes.models import ContentType
from django.template import Variable
from django.core.urlresolvers import reverse

from zorna.acl.models import get_allowed_objects, get_acl_by_object
    
register = template.Library() 

class check_permission_node( template.Node ):
    def __init__(self, app_name, model, permission, var_name):
        self.permission = permission
        self.var_name = var_name
        self.app_name = app_name
        self.model = model
        
    def render(self, context):
        request = context['request']
        try:
            ct = ContentType.objects.get(app_label= self.app_name, model=self.model)
            ob = get_allowed_objects(request.user, ct.model_class(), self.permission)
            context[self.var_name] = ob
        except:
            pass
        return ''
    
@register.tag(name="check_permission")        
def check_permission( parser, token ):
    bits = token.split_contents()
    if 6 != len(bits):
        raise TemplateSyntaxError('%r expects 6 arguments' % bits[0])
    if bits[-2] != 'as':
        raise TemplateSyntaxError(
            '%r expects "as" as the second argument' % bits[0])
    app_name = bits[1]
    model = bits[2]
    permission = bits[3]
    varname = bits[-1]
    return check_permission_node(app_name, model, permission, varname)

    
class acl_groups_object_node( template.Node ):
    def __init__(self, obj):
        self.obj = Variable(obj)
        
    def render(self, context):
        obj = self.obj.resolve(context)
        #try:
        ct = ContentType.objects.get_for_model(obj)
        return reverse('acl_groups_object', args=[ct.id, obj.id])
        #except:
        #    pass
        #return ''
    
@register.tag(name="acl_groups_object_url")        
def acl_groups_object( parser, token ):
    bits = token.split_contents()
    if 2 != len(bits):
        raise TemplateSyntaxError('%r expects 2 arguments' % bits[0])
    obj = bits[-1]
    return acl_groups_object_node(obj)

class acl_users_object_node( template.Node ):
    def __init__(self, obj):
        self.obj = Variable(obj)
        
    def render(self, context):
        obj = self.obj.resolve(context)
        #try:
        ct = ContentType.objects.get_for_model(obj)
        return reverse('acl_users_object', args=[ct.id, obj.id])
        #except:
        #    pass
        #return ''
    
@register.tag(name="acl_users_object_url")        
def acl_users_object( parser, token ):
    bits = token.split_contents()
    if 2 != len(bits):
        raise TemplateSyntaxError('%r expects 2 arguments' % bits[0])
    obj = bits[-1]
    return acl_users_object_node(obj)

class get_users_by_permission_node( template.Node ):
    def __init__(self, obj, permission, var_name):
        self.obj = Variable(obj)
        self.permission = permission
        self.var_name = var_name
        
    def render(self, context):
        context[self.var_name] = get_acl_by_object(self.obj.resolve(context), self.permission)
        return ''


@register.tag(name="get_users_by_permission")        
def get_users_by_permission( parser, token ):
    """
    {% get_users_by_permission object permission as variable %}
    """
    bits = token.split_contents()
    if 5 != len(bits):
        raise TemplateSyntaxError('%r expects 5 arguments' % bits[0])
    if bits[-2] != 'as':
        raise TemplateSyntaxError(
            '%r expects "as" as the second argument' % bits[0])
    obj = bits[1]
    permission = bits[2]
    varname = bits[-1]
    return get_users_by_permission_node(obj, permission, varname)