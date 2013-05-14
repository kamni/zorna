import os
try: 
    from PIL import Image
except ImportError: 
    import Image

from django.conf import settings
from django.template import TemplateSyntaxError
from django import template
from django.contrib.auth.models import User
from django.utils import simplejson
from django.template import Variable

from zorna.forms.models import FormsForm, FormsFormEntry
from zorna.forms.api import forms_get_entry

register = template.Library() 


SCALE_WIDTH = 'w'
SCALE_HEIGHT = 'h'
SCALE_BOTH = 'both'

def scale(max_x, pair):
    x, y = pair
    new_y = (float(max_x) / x) * y
    return (int(max_x), int(new_y))

@register.filter
def thumbnail(file, size='200w'):
    """
    Credits: 
    http://djangosnippets.org/snippets/1238/
    """
    # defining the size
    if (size.lower().endswith('h')):
        mode = 'h'
        size = size[:-1]
        max_size = int(size.strip())
    elif (size.lower().endswith('w')):
        mode = 'w'
        size = size[:-1]
        max_size = int(size.strip())
    else:
        mode = 'both'
        
    # defining the filename and the miniature filename
    filehead, filetail = os.path.split(file.path)
    basename, format = os.path.splitext(filetail)
    miniature = basename + '_' + size + format
    filename = file.path
    miniature_filename = os.path.join(filehead, miniature)
    filehead, filetail = os.path.split(file.name)
    miniature_url = filehead + '/' + miniature
    if os.path.exists(miniature_filename) and os.path.getmtime(filename)>os.path.getmtime(miniature_filename):
        os.unlink(miniature_filename)
    # if the image wasn't already resized, resize it
    if not os.path.exists(miniature_filename):
        image = Image.open(filename)
        image_x, image_y = image.size  
        
        if mode == SCALE_HEIGHT:
            image_y, image_x = scale(max_size, (image_y, image_x))
        elif mode == SCALE_WIDTH:
            image_x, image_y = scale(max_size, (image_x, image_y))
        elif mode == SCALE_BOTH:
            image_x, image_y = [int(x) for x in size.split('x')]
        else:
            raise Exception("Thumbnail size must be in ##w, ##h, or ##x## format.")
            
        image.thumbnail([image_x, image_y], Image.ANTIALIAS)
        try:
            image.save(miniature_filename, image.format, quality=90, optimize=1)
        except:
            image.save(miniature_filename, image.format, quality=90)

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
    data = [ ("%s %s" % (x.last_name, x.first_name), x.id) for x in objects ]
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
    users_list = [ ("%s %s" % (x.last_name, x.first_name), x.id) for x in objects ]
    json_data = simplejson.dumps(users_list)    
    return locals()

json_list_users = register.inclusion_tag(
    'account/ac_json_users.html',
    takes_context=True
)(json_list_users)

class get_user_profile_node( template.Node ):
    def __init__(self, user_varname, columns_varname, rows_varname):
        self.columns_varname = columns_varname
        self.rows_varname = rows_varname
        self.user_varname = Variable(user_varname)
    
    def render(self, context):
        try:
            form = FormsForm.objects.get(slug=settings.ZORNA_USER_PROFILE_FORM)
            try:
                entry = form.entries.get(account__id=self.user_varname.resolve(context))
            except FormsFormEntry.DoesNotExist:
                entry = None
        except Exception as e:
            entry = None
        if entry:
            context[self.columns_varname], context[self.rows_varname] = forms_get_entry(entry)
        else:
            context[self.columns_varname] = None
            context[self.rows_varname] = None
        return ''
    
@register.tag(name="get_user_profile")        
def get_user_profile( parser, token ):
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