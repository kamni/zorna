from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify
from django.http import Http404, HttpResponse
from django.utils import simplejson
from zorna.faq.models import Faq, FaqCategory, FaqQuestion
from zorna.faq.forms import FaqQuestionCategoryForm, FaqForm, FaqQuestionForm
from zorna.acl.models import get_allowed_objects, get_acl_for_model


@login_required()
def list_faqs(request):
    if request.user.is_superuser:
        ob_list = Faq.objects.all()
        extra_context ={}
        extra_context['faq_list'] = ob_list
        context = RequestContext(request)
        return render_to_response('faq/list_faqs.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')

@login_required()
def admin_add_faq(request):
    if request.user.is_superuser:
        if request.method == 'POST':    
            form = FaqForm(request.POST)
            if form.is_valid():
                faq = form.save(commit=False)
                faq.owner = request.user
                faq.save()
                return HttpResponseRedirect(reverse('list_faqs'))
            else:
                form = FaqForm(request.POST)
        else:
            form = FaqForm()
            
        context = RequestContext(request)
        extra_context = {'form': form, 'curfaq': False}
        return render_to_response('faq/edit_faq.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')

@login_required()
def admin_edit_faq(request, faq):
    if request.user.is_superuser:
        c = Faq.objects.get(pk=faq)
        if request.method == 'POST':    
            form = FaqForm(request.POST, instance=c)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('admin_list_categories'))
        else:
            form = FaqForm(instance=c)
            
        context = RequestContext(request)
        extra_context = {'form': form, 'curfaq': c}
        return render_to_response('faq/edit_faq.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')

def manager_list_faqs(request):
    aom = get_allowed_objects(request.user, Faq, 'manager')
    aoc = get_allowed_objects(request.user, Faq, 'reader')
    allowed_objects = list(set(aom) | set(aoc))
    if len(allowed_objects) ==  0:
        return HttpResponseRedirect('/')
    ob_list = Faq.objects.filter(pk__in=allowed_objects)
    for ob in ob_list:
        if ob.pk in aom:
            ob.manager = True
        else:
            ob.manager = False
    extra_context ={}
    extra_context['faq_list'] = ob_list
    context = RequestContext(request)
    return render_to_response('faq/manager_list_faqs.html', extra_context, context_instance=context)

@login_required()
def manager_edit_faq(request, faq):
    try:
        faq = Faq.objects.get(pk=faq)
    except Faq.DoesNotExist:
        raise Http404
    check = get_acl_for_model(Faq)
    if check.manager_faq(faq, request.user):    
        ob_list = FaqCategory.objects.filter(faq=faq)
        extra_context ={}
        extra_context['categories'] = ob_list
        extra_context['curfaq'] = faq
        context = RequestContext(request)
        return render_to_response('faq/manager_edit_faq.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')

@login_required()
def manager_faq_list_categories(request, faq):
    try:
        faq = Faq.objects.get(pk=faq)
    except Faq.DoesNotExist:
        raise Http404
    check = get_acl_for_model(Faq)
    if check.manager_faq(faq, request.user):    
        ob_list = FaqCategory.objects.filter(faq__pk=faq.pk)
        extra_context ={}
        extra_context['categories'] = ob_list
        extra_context['curfaq'] = faq
        context = RequestContext(request)
        return render_to_response('faq/list_categories.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')

@login_required()
def manager_faq_add_category(request, faq):
    try:
        faq = Faq.objects.get(pk=faq)
    except Faq.DoesNotExist:
        raise Http404
    check = get_acl_for_model(Faq)
    if check.manager_faq(faq, request.user):    
        initial_data = {}
        initial_data['faq'] = faq
        if request.method == 'POST':    
            form = FaqQuestionCategoryForm(request, request.POST, initial=initial_data)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('manager_faq_list_categories', args=[faq.pk]))
            else:
                form = FaqQuestionCategoryForm(request, request.POST, initial=initial_data)
        else:
            form = FaqQuestionCategoryForm(request, initial=initial_data)
            
        context = RequestContext(request)
        extra_context = {'form': form, 'curcategory': False}
        extra_context['curfaq'] = Faq.objects.get(pk=faq.pk)
        return render_to_response('faq/edit_category.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')

@login_required()
def manager_faq_edit_category(request, category):
    try:
        category = FaqCategory.objects.get(pk=category)
    except FaqCategory.DoesNotExist:
        raise Http404
    check = get_acl_for_model(Faq)
    if check.manager_faq(category.faq, request.user):    
        if request.method == 'POST':    
            form = FaqQuestionCategoryForm(request, request.POST, instance=category)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('manager_faq_list_categories', args=[category.faq_id]))
            else:
                form = FaqQuestionCategoryForm(request, request.POST, instance=category)
        else:
            form = FaqQuestionCategoryForm(request, instance=category)
            
        context = RequestContext(request)
        extra_context = {'form': form, 'curcategory': category}
        extra_context['curfaq'] = category.faq
        return render_to_response('faq/edit_category.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')
    
@login_required()    
def manager_faq_list_questions(request, category):
    try:
        category = FaqCategory.objects.get(pk=category)
    except Faq.DoesNotExist:
        raise Http404
    check = get_acl_for_model(Faq)
    if check.manager_faq(category.faq, request.user):    
        ob_list = FaqQuestion.objects.filter(category=category)
        extra_context ={}
        extra_context['questions'] = ob_list
        extra_context['curfaq'] = category.faq
        extra_context['curcategory'] = category
        context = RequestContext(request)
        return render_to_response('faq/list_questions.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')  

@login_required()    
def manager_faq_add_question(request, faq, category=None):
    try:
        faq = Faq.objects.get(pk=faq)
        if category:
            category = FaqCategory.objects.get(pk=category)
    except FaqCategory.DoesNotExist:
        raise Http404
    check = get_acl_for_model(Faq)
    if check.manager_faq(faq, request.user):    
        initial_data = {}
        initial_data['category'] = category.pk if category else None
        if request.method == 'POST':    
            form = FaqQuestionForm(request, faq, request.POST, initial=initial_data)
            if form.is_valid():
                question = form.save(commit=False)
                question.owner = request.user
                question.slug = slugify(question.question)        
                question.save()
                return HttpResponseRedirect(reverse('manager_edit_faq', args=[faq.pk]))
            else:
                form = FaqQuestionForm(request, faq, request.POST, initial=initial_data)
        else:
            form = FaqQuestionForm(request, faq, initial=initial_data)
            
        context = RequestContext(request)
        extra_context = {'form': form, 'curcategory': category}
        extra_context['curfaq'] = faq
        extra_context['curquestion'] = False
        return render_to_response('faq/edit_question.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')

@login_required()
def manager_faq_edit_question(request, question):
    try:
        question = FaqQuestion.objects.get(pk=question)
        category = question.category
        faq = category.faq
    except FaqCategory.DoesNotExist:
        raise Http404
    check = get_acl_for_model(Faq)
    if check.manager_faq(faq, request.user):    
        initial_data = {}
        initial_data['category'] = category.pk
        if request.method == 'POST':    
            if request.POST.has_key('bdelete'):
                question.delete()
                return HttpResponseRedirect(reverse('manager_edit_faq', args=[faq.pk]))
            form = FaqQuestionForm(request, faq, request.POST, initial=initial_data, instance=question)
            if form.is_valid():
                question = form.save(commit=False)
                question.owner = request.user
                question.slug = slugify(question.question)        
                question.save()
                return HttpResponseRedirect(reverse('manager_edit_faq', args=[faq.pk]))
            else:
                form = FaqQuestionForm(request, faq, request.POST, initial=initial_data, instance=question)
        else:
            form = FaqQuestionForm(request, faq, initial=initial_data, instance=question)
            
        context = RequestContext(request)
        extra_context = {'form': form, 'curcategory': category}
        extra_context['curfaq'] = faq
        extra_context['curquestion'] = True
        return render_to_response('faq/edit_question.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')

@login_required()
def sort_faq_questions(request, category):
    questions = request.GET.getlist('category-table-dnd[]')
    sort_order = 1
    ret = {}
    ret['error'] = False
    try:
        for q in questions:
            if q:
                c = FaqQuestion.objects.get(pk=q)
                c.sort_order = sort_order;
                c.save()
                sort_order += 1
    except:
        pass
    return HttpResponseRedirect(reverse('manager_faq_list_questions', args=[category]))


@login_required()
def sort_faq_categories(request, faq):
    categories = request.GET.getlist('category-table-dnd[]')
    sort_order = 1
    ret = {}
    ret['error'] = False
    try:
        for cat in categories:
            if cat:
                c = FaqCategory.objects.get(pk=int(cat))
                c.sort_order = sort_order;
                c.save()
                sort_order += 1
    except:
        pass
    return HttpResponseRedirect(reverse('manager_faq_list_categories', args=[faq]))

def browse_faq(request, faqslug):
    slugs = faqslug.split('/')
    try:
        faq = Faq.objects.get(slug=slugs[0])
        if len(slugs) > 1:
            category = FaqCategory.objects.get(slug=slugs[1], faq = faq)
        else:
            category = None
    except Faq.DoesNotExist or FaqCategory.DoesNotExist:
        raise Http404
    check = get_acl_for_model(Faq)
    if check.reader_faq(faq, request.user):    
        ob_list = FaqCategory.objects.filter(faq=faq)
        extra_context ={}
        extra_context['categories'] = ob_list
        extra_context['curfaq'] = faq
        extra_context['curcategory'] = category
        context = RequestContext(request)
        return render_to_response('faq/browse_faq.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')

            
