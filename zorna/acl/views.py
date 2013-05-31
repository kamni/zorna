# Create your views here.
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType

from zorna.acl.models import get_acl_for_model
from zorna import defines


def get_acl_forms(request, object, **kwargs):
    if request.user.is_superuser:
        check = get_acl_for_model(object)
        return check.get_acl_groups_forms(request, object.pk, **kwargs)
    else:
        return HttpResponseRedirect('/')


def acl_groups_object(request, ct, object):
    ct = ContentType.objects.get(pk=ct)
    object = ct.get_object_for_this_type(pk=object)
    return get_acl_forms(request, object)


def acl_gte_registered_object(request, object):
    kwargs = {'exclude': [defines.ZORNA_GROUP_REGISTERED]}
    return get_acl_forms(request, object, **kwargs)


def acl_users_object(request, ct, object):
    if request.user.is_superuser:
        ct = ContentType.objects.get(pk=ct)
        object = ct.get_object_for_this_type(pk=object)
        check = get_acl_for_model(object)
        return check.get_acl_users_forms(request, object.pk, template='acl/admin_acl_users.html')
    else:
        return HttpResponseRedirect('/')
