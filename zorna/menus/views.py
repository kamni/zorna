from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType

from zorna.menus.models import ZornaMenuItem
from zorna.site.models import SiteOptions
from zorna.menus.forms import ZornaMenuItemUrlForm, ZornaMenuItemArticleCategoryForm, ZornaMenuItemFaqForm, ZornaMenuItemFormsForm, ZornaMenuItemPageContentForm


def user_has_access_to_menus(user):
    return SiteOptions.objects.is_access_valid(user, 'zorna_menus')


@login_required()
def menus_home_view(request):
    if user_has_access_to_menus(request.user):
        ob_list = ZornaMenuItem.objects.all()
        extra_context = {}
        extra_context['items_list'] = ob_list
        context = RequestContext(request)
        return render_to_response('menus/menus_home.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')

@login_required()
def menus_add_item_url(request):
    if user_has_access_to_menus(request.user):
        if request.method == 'POST':
            form = ZornaMenuItemUrlForm(request.POST)
            if form.is_valid():
                item = form.save(commit=False)
                item.url = form.cleaned_data['url']
                item.save()
                return HttpResponseRedirect(reverse('menus_home_view'))
            else:
                form = ZornaMenuItemUrlForm(request.POST)
        else:
            form = ZornaMenuItemUrlForm()

        context = RequestContext(request)
        extra_context = {'form': form, 'curitem': False, 'title': _(u'Add a link')}
        return render_to_response('menus/edit_menu_item.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')

@login_required()
def menus_edit_item_url(request, item):
    if request.method == 'POST':
        form = ZornaMenuItemUrlForm(request.POST, instance=item, initial={'url': item.url})
        if form.is_valid():
            item = form.save(commit=False)
            item.url = form.cleaned_data['url']
            item.save()
            return HttpResponseRedirect(reverse('menus_home_view'))
        else:
            form = ZornaMenuItemUrlForm(request.POST, instance=item, initial={'url': item.url})
    else:
        form = ZornaMenuItemUrlForm(instance=item, initial={'url': item.url})

    context = RequestContext(request)
    extra_context = {'form': form, 'curitem': item}
    return render_to_response('menus/edit_menu_item.html', extra_context, context_instance=context)

@login_required()
def menus_add_item_article_category(request):
    if user_has_access_to_menus(request.user):
        if request.method == 'POST':
            form = ZornaMenuItemArticleCategoryForm(request.POST)
            if form.is_valid():
                item = form.save(commit=False)
                item.content_object = form.cleaned_data['category']
                item.save()
                return HttpResponseRedirect(reverse('menus_home_view'))
            else:
                form = ZornaMenuItemArticleCategoryForm(request.POST)
        else:
            form = ZornaMenuItemArticleCategoryForm()

        context = RequestContext(request)
        extra_context = {'form': form, 'curitem': False, 'title': _(u'Add a link to an articles category')}
        return render_to_response('menus/edit_menu_item.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')

@login_required()
def menus_edit_item_article_category(request, item):
    if request.method == 'POST':
        form = ZornaMenuItemArticleCategoryForm(request.POST, instance=item, initial={'category': item.object_id})
        if form.is_valid():
            item = form.save(commit=False)
            item.content_object = form.cleaned_data['category']
            item.save()
            return HttpResponseRedirect(reverse('menus_home_view'))
        else:
            form = ZornaMenuItemArticleCategoryForm(request.POST, instance=item, initial={'category': item.object_id})
    else:
        form = ZornaMenuItemArticleCategoryForm(instance=item, initial={'category': item.object_id})

    context = RequestContext(request)
    extra_context = {'form': form, 'curitem': item}
    return render_to_response('menus/edit_menu_item.html', extra_context, context_instance=context)


@login_required()
def menus_add_item_faq(request):
    if user_has_access_to_menus(request.user):
        if request.method == 'POST':
            form = ZornaMenuItemFaqForm(request.POST)
            if form.is_valid():
                item = form.save(commit=False)
                item.content_object = form.cleaned_data['faq']
                item.save()
                return HttpResponseRedirect(reverse('menus_home_view'))
            else:
                form = ZornaMenuItemFaqForm(request.POST)
        else:
            form = ZornaMenuItemFaqForm()

        context = RequestContext(request)
        extra_context = {'form': form, 'curitem': False, 'title': _(u'Add a link to faq')}
        return render_to_response('menus/edit_menu_item.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')

@login_required()
def menus_edit_item_faq(request, item):
    if request.method == 'POST':
        form = ZornaMenuItemFaqForm(request.POST, instance=item, initial={'faq': item.object_id})
        if form.is_valid():
            item = form.save(commit=False)
            item.content_object = form.cleaned_data['faq']
            item.save()
            return HttpResponseRedirect(reverse('menus_home_view'))
        else:
            form = ZornaMenuItemFaqForm(request.POST, instance=item, initial={'faq': item.object_id})
    else:
        form = ZornaMenuItemFaqForm(instance=item, initial={'faq': item.object_id})

    context = RequestContext(request)
    extra_context = {'form': form, 'curitem': item}
    return render_to_response('menus/edit_menu_item.html', extra_context, context_instance=context)


@login_required()
def menus_add_item_form_submission(request):
    if user_has_access_to_menus(request.user):
        if request.method == 'POST':
            form = ZornaMenuItemFormsForm(request.POST)
            if form.is_valid():
                item = form.save(commit=False)
                item.content_object = form.cleaned_data['form']
                item.extra_info = 'submission'
                item.save()
                return HttpResponseRedirect(reverse('menus_home_view'))
            else:
                form = ZornaMenuItemFormsForm(request.POST)
        else:
            form = ZornaMenuItemFormsForm()

        context = RequestContext(request)
        extra_context = {'form': form, 'curitem': False, 'title': _(u'Add a link to form submission')}
        return render_to_response('menus/edit_menu_item.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')

@login_required()
def menus_add_item_form_browse(request):
    if user_has_access_to_menus(request.user):
        if request.method == 'POST':
            form = ZornaMenuItemFormsForm(request.POST)
            if form.is_valid():
                item = form.save(commit=False)
                item.content_object = form.cleaned_data['form']
                item.extra_info = 'browse'
                item.save()
                return HttpResponseRedirect(reverse('menus_home_view'))
            else:
                form = ZornaMenuItemFormsForm(request.POST)
        else:
            form = ZornaMenuItemFormsForm()

        context = RequestContext(request)
        extra_context = {'form': form, 'curitem': False, 'title': _(u'Add a link to form list')}
        return render_to_response('menus/edit_menu_item.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')


@login_required()
def menus_edit_item_form(request, item):
    if request.method == 'POST':
        form = ZornaMenuItemFormsForm(request.POST, instance=item, initial={'form': item.object_id})
        if form.is_valid():
            item = form.save(commit=False)
            item.content_object = form.cleaned_data['form']
            item.save()
            return HttpResponseRedirect(reverse('menus_home_view'))
        else:
            form = ZornaMenuItemFormsForm(request.POST, instance=item, initial={'form': item.object_id})
    else:
        form = ZornaMenuItemFormsForm(instance=item, initial={'form': item.object_id})
    if item.extra_info == 'submission':
        form.fields['form'].label = _(u"Form submission")
    else:
        form.fields['form'].label = _(u"Form browse")

    context = RequestContext(request)
    extra_context = {'form': form, 'curitem': item}
    return render_to_response('menus/edit_menu_item.html', extra_context, context_instance=context)

@login_required()
def menus_add_item_page_content(request):
    if user_has_access_to_menus(request.user):
        form = ZornaMenuItemPageContentForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            item = form.save(commit=False)
            item.url = form.cleaned_data['page']
            item.save()
            return HttpResponseRedirect(reverse('menus_home_view'))

        context = RequestContext(request)
        extra_context = {'form': form, 'curitem': False, 'title': _(u'Add a link to page content')}
        return render_to_response('menus/edit_menu_item.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')


@login_required()
def menus_edit_item(request, item_id):
    if user_has_access_to_menus(request.user):
        item = ZornaMenuItem.objects.get(pk=item_id)
        if request.method == 'POST' and request.POST.has_key('bdelete'):
            item.delete()
            return HttpResponseRedirect(reverse('menus_home_view'))
        if request.method == 'POST' and request.POST.has_key('childs_ids') and request.POST['childs_ids']:
            ids = request.POST['childs_ids'].split(',')
            last_m = ZornaMenuItem.objects.get(pk=ids.pop(0))
            last_m.move_to(last_m.parent, position='first-child')
            for id in ids:
                last_m = ZornaMenuItem.objects.get(pk=last_m.id)
                m = ZornaMenuItem.objects.get(pk=id)
                m.move_to(last_m, position='right')
                last_m = m

        if item.object_id:
            if item.content_type == ContentType.objects.get(model='articlecategory'):
                return menus_edit_item_article_category(request, item)
            elif item.content_type == ContentType.objects.get(model='faq'):
                return menus_edit_item_faq(request, item)
            elif item.content_type == ContentType.objects.get(model='formsform'):
                return menus_edit_item_form(request, item)
        else:
            return menus_edit_item_url(request, item)
    else:
        return HttpResponseRedirect('/')
