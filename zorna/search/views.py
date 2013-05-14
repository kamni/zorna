from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404

from haystack.query import SearchQuerySet
from zorna.acl.models import get_allowed_objects
from zorna.articles.models import ArticleCategory, ArticleStory
from zorna.faq.models import FaqQuestion, Faq
from zorna.search.form import SearchForm

RESULTS_PER_PAGE = 15


def search(request):
    results_articles = None
    results_faqs = None
    results = {}
    query = ''
    if request.GET.get('q'):
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['q']
            what= request.GET.get('what', None)
            if what == 'articles' or what == None:
                ao = get_allowed_objects(request.user, ArticleCategory, 'reader')
                ao = [str(p) for p in ao]
                results_articles = SearchQuerySet().filter(content=query).filter(categories__in=ao).models(ArticleStory)
                if results_articles:
                    paginator = Paginator(results_articles, RESULTS_PER_PAGE)
                    try:
                        page = paginator.page(int(request.GET.get('page', 1)))
                    except InvalidPage:
                        raise Http404("No such page of results!")
                    results['articles'] = {'results': results_articles, 'page': page, 'paginator': paginator }
        
            if what == 'faqs' or what == None:
                ao = get_allowed_objects(request.user, Faq, 'reader')
                ao = [str(p) for p in ao]
                results_faqs = SearchQuerySet().filter(content=query).filter(faq__in=ao).models(FaqQuestion)
                if results_faqs:
                    paginator = Paginator(results_faqs, RESULTS_PER_PAGE)
                    try:
                        page = paginator.page(int(request.GET.get('page', 1)))
                    except InvalidPage:
                        raise Http404("No such page of results!")
                    results['faqs'] = {'results': results_faqs, 'page': page, 'paginator': paginator }
    else:
        form = SearchForm()
    
    context = RequestContext(request)
    extra_context = {
                    'form': form, 
                    'results': results,
                    'query': query,
                    }
    return render_to_response('search/search.html', extra_context, context_instance=context)
            