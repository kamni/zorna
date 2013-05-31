import shutil
import os
import re
import datetime
import urllib
import posixpath
from django.utils.translation import ugettext_noop
from django.utils.encoding import smart_str
from django.template.defaultfilters import slugify
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.template.loader import get_template
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template import Template
from django.template.loader_tags import BlockNode

from zorna.pages.forms import PageEditTemplateForm, PageEditFileForm, PageEditFileContextForm
from zorna.site.models import SiteOptions


def normalize_path(path):
    path = posixpath.normpath(urllib.unquote(path))
    path = path.lstrip('/')
    newpath = ''
    for part in path.split('/'):
        if not part:
            # Strip empty path components.
            continue
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')
    return newpath


def get_pages_access(user):
    b_pages_manager = SiteOptions.objects.is_access_valid(
        user, 'zorna_pages_pages')
    b_templates_manager = SiteOptions.objects.is_access_valid(
        user, 'zorna_pages_templates')
    return b_pages_manager, b_templates_manager


def fmbrowser_home(request):
    extra_context = {}
    extra_context['pages_manager'], extra_context[
        'templates_manager'] = get_pages_access(request.user)
    baccess = extra_context[
        'pages_manager'] or extra_context['templates_manager']
    if baccess:
        extra_context['file_type'] = request.GET.get('file_type', 'file')
        extra_context['dir'] = request.GET.get('dir', '')
        context = RequestContext(request)
        return render_to_response('pages/fmbrowser_home.html', extra_context, context_instance=context)
    else:
        return HttpResponseForbidden()


def dirlist(request, path, template=True):
    r = ['<ul class="jqueryFileTree" style="display: none;">']
    try:
        path = normalize_path(path)
        if template:
            file_type = 'template'
            root = settings.PROJECT_PATH + os.sep + 'skins' + os.sep
        else:
            file_type = 'file'
            root = settings.PROJECT_PATH + \
                os.sep + settings.ZORNA_CONTENT + os.sep
        d = root + path
        if path:
            rel = path + '/'
        else:
            rel = ''
        folders = []
        files = []
        for f in os.listdir(d):
            ff = os.path.join(d, f)
            if os.path.isdir(ff):
                folders.append(f)
            else:
                files.append(f)
        folders.sort()
        files.sort()
        help_txt = ugettext_noop(u'Double click to open or close folder')
        for f in folders:
            if template and settings.ZORNA_SKIN == f:
                r.append('<li class="directory collapsed"><a href="#" rel="%s%s/" title="%s"><b>%s</b></a></li>' % (
                    rel, f, help_txt, f))
            else:
                r.append('<li class="directory collapsed"><a href="#" rel="%s%s/" title="%s">%s</a></li>' % (
                    rel, f, help_txt, f))
        help_txt = ugettext_noop(u'Double click to edit file')
        for f in files:
            e = os.path.splitext(f)[1][1:]  # get .ext and remove dot
            r.append('<li class="%s ext_%s"><a href="#" rel="%s%s" title="%s">%s</a></li>' %
                     (file_type, e, rel, f, help_txt, f))
    except Exception, e:
        r.append('Could not load directory: %s' % str(e))
    r.append('</ul>')
    return ''.join(r)


def dirlist_files(request):
    b_pages_manager, b_templates_manager = get_pages_access(request.user)
    if b_pages_manager:
        cdir = request.GET.get('dir', '')
        return HttpResponse(dirlist(request, cdir, False))
    else:
        return HttpResponse('')


def dirlist_templates(request):
    b_pages_manager, b_templates_manager = get_pages_access(request.user)
    if b_templates_manager:
        cdir = request.GET.get('dir', '')
        return HttpResponse(dirlist(request, cdir, True))
    else:
        return HttpResponse('')


def edit_template(request, template=True):
    b_pages_manager, b_templates_manager = get_pages_access(request.user)
    if b_pages_manager or b_templates_manager:
        template_file = request.REQUEST.get('file', '')
        if template and b_templates_manager:
            url_action = reverse('edit_template')
            path_tf = settings.PROJECT_PATH + os.sep + 'skins' + os.sep
        else:
            url_action = reverse('edit_source_file')
            path_tf = os.path.join(
                settings.PROJECT_PATH, settings.ZORNA_CONTENT) + os.sep
        path_tf = path_tf + template_file
        if request.method == 'POST':
            try:
                text = request.REQUEST.get('body', '')
                ft = open(path_tf, 'w')
                ft.write(text.encode('UTF-8'))
                ft.close()
                ret = {'status': 'success', 'message':
                       "Your template has been updated"}
                return HttpResponse(simplejson.dumps(ret))
            except Exception as e:
                ret = {'status': 'error', 'message': 'Error: %s' % str(e)}
                return HttpResponse(simplejson.dumps(ret))

        try:
            ft = open(path_tf, 'r')
            text = ft.read()
            ft.close()
        except Exception as e:
            template_file = text = ''

        form = PageEditTemplateForm(initial={'body': text})
        extra_context = {'form': form,
                         'template_file': template_file,
                         'text': text,
                         'cdir_components': format_components(template_file),
                         'url_action': url_action,
                         'template': template}
        context = RequestContext(request)
        return render_to_response('pages/fm_edit_template.html', extra_context, context_instance=context)
    else:
        return HttpResponse('')


def edit_source_file(request):
    return edit_template(request, False)


def get_editable_blocks(template):
    t = get_template(template)
    blocks = t.nodelist.get_nodes_by_type(BlockNode)
    ret = {}
    for b in blocks:
        if b.name[0:2] == '__':
            ret[b.name] = ''
    return ret


def get_blocks(request, template_string):
    t = Template(template_string)
    ret = []
    '''
    extends = t.nodelist.get_nodes_by_type(ExtendsNode)
    for ex in extends:
        ret = dict(ret.items() + get_editable_blocks(ex.parent_name).items())
    '''
    context = RequestContext(request)
    for b in t.nodelist.get_nodes_by_type(BlockNode):
        if b.name[0:2] == '__':
            ret.append({
                       'block': b.name, 'content': b.nodelist.render(context)})
    return ret


def preview_page(request, path):
    from zorna.utils import render_page
    page = render_page(request, path)
    path_tf = os.path.join(
        settings.PROJECT_PATH, settings.ZORNA_CONTENT, path + '.html')
    os.remove(path_tf)
    return HttpResponse(page)


def edit_page(request):
    b_pages_manager, b_templates_manager = get_pages_access(request.user)
    if b_pages_manager:
        from zorna.utils import get_context_text
        page = request.REQUEST.get('file', '')
        path_tf = os.path.join(
            settings.PROJECT_PATH, settings.ZORNA_CONTENT, page)
        header, text = get_context_text(path_tf)
        blocks = get_blocks(request, text)
        import yaml
        context_yaml = yaml.load(header)
        if request.method == 'POST':
            try:
                import codecs
                lflr = '\r\n'
                fd = codecs.open(path_tf, "r+", "utf-8")
                text = fd.read()
                to_add = []
                for key, value in request.POST.iteritems():
                    if key[0:2] == '__':
                        repl = "%s block %s %s\n%s\n%s endblock %s" % (
                            '{%', key, '%}', value, '{%', '%}')
                        pre = re.compile(r'(%s\s*block\s*%s\s*%s)(.*?)(%s\s*endblock.*?\s*%s)' % (re.escape(
                            '{%'), key, re.escape('%}'), re.escape('{%'), re.escape('%}')), re.M | re.DOTALL)
                        if pre.search(text):
                            text = pre.sub(repl, text)
                        else:
                            to_add.append(repl + lflr)

                description = request.POST.get(
                    "description", '').replace('\n', '')
                tab_ctx = {'title': request.POST.get("title", ''), 'description': description, 'keywords': request.POST.get(
                    "keywords", ''), 'created': str(datetime.datetime.now()), 'author': str(request.user.pk)}
                if not header:
                    context_yaml = tab_ctx
                else:
                    context_yaml.update(tab_ctx)
                result = ''
                for k, v in context_yaml.iteritems():
                    if k in request.POST:
                        v = request.POST.get(k, '').replace('\n', '')
                    result = result + k + ": '%s'%s" % (
                        v.replace("'", "''"), lflr)
                ctx = "%s zorna %s%s%s%s" % ('{%', lflr, result, lflr, '%}')
                pre = re.compile(r'(%s\s*zorna)(.*?)(\s*%s)' % (
                    re.escape('{%'), re.escape('%}')), re.M | re.DOTALL)
                if pre.search(text):
                    text = pre.sub(ctx, text)
                else:
                    text = text + lflr + ctx

                what = request.REQUEST.get('what', 'save')
                if what == 'save':
                    fd.seek(0)
                    fd.truncate()
                    fd.write(text)
                    fd.close()
                else:
                    # create temporary file
                    head, tail = os.path.split(page)
                    if head:
                        head = head + '/'
                    temp_page = head + 'temp-%s' % tail
                    path_tempf = os.path.join(
                        settings.PROJECT_PATH, settings.ZORNA_CONTENT, temp_page)
                    fd = open(path_tempf, 'w+')
                    fd.write(text.encode('UTF-8'))
                    fd.close()
                    return HttpResponseRedirect(reverse('preview_page', args=[os.path.splitext(temp_page)[0]]))
            except Exception as e:
                ret = {'status': 'error', 'message': 'Error: %s' % str(e)}
                return HttpResponse(simplejson.dumps(ret))

            ret = {'status': 'success', 'message':
                   'Your changes have been saved successfully.'}
            return HttpResponse(simplejson.dumps(ret))

        form = PageEditFileForm(extra=blocks)
        if header:
            initial_data = {}
            initial_data['title'] = context_yaml[
                'title'] if 'title' in context_yaml else ''
            initial_data['description'] = context_yaml[
                'description'] if 'description' in context_yaml else ''
            initial_data['keywords'] = context_yaml[
                'keywords'] if 'keywords' in context_yaml else ''
            for e in ['author', 'created', 'title', 'keywords', 'description']:
                if e in context_yaml:
                    del context_yaml[e]
            form_context = PageEditFileContextForm(
                initial=initial_data, extra=context_yaml)
        else:
            form_context = None
        extra_context = {'form_context': form_context, 'form':
                         form, 'cdir_components': format_components(page), 'template_file': page}
        context = RequestContext(request)
        return render_to_response('pages/fm_edit_file.html', extra_context, context_instance=context)
    else:
        return HttpResponse('')


def format_components(cdir):
    cdir_components = []
    if cdir:
        path = None
        for comp in cdir.split('/'):
            if path:
                path = path + comp + '/'
            else:
                path = comp + '/'
            cdir_components.append({'rel': path, 'text': comp})
    else:
        cdir_components = []
    return cdir_components


def dirlist_folder(request, file_type):
    cdir = request.REQUEST.get('dir', '')
    cdir = normalize_path(cdir)
    if file_type == 'template':
        path = settings.PROJECT_PATH + os.sep + 'skins' + os.sep
    else:
        path = settings.PROJECT_PATH + os.sep + settings.ZORNA_CONTENT + os.sep
    path = path + cdir
    try:
        files = []
        for f in os.listdir(path):
            ff = os.path.join(path, f)
            if os.path.isdir(ff):
                pass
            else:
                files.append(os.path.splitext(f)[0])
    except Exception as e:
        return HttpResponse(smart_str(e))

    files.sort()
    extra_context = {'files': files, 'cdir_components':
                     format_components(cdir), 'cdir': cdir, 'file_type': file_type}
    context = RequestContext(request)
    return render_to_response('pages/fm_manage_folder.html', extra_context, context_instance=context)


def dirlist_folder_files(request):
    b_pages_manager, b_templates_manager = get_pages_access(request.user)
    if b_pages_manager:
        return dirlist_folder(request, 'file')
    else:
        return HttpResponse('')


def dirlist_folder_templates(request):
    b_pages_manager, b_templates_manager = get_pages_access(request.user)
    if b_templates_manager:
        return dirlist_folder(request, 'template')
    else:
        return HttpResponse('')


def clone_webpage(request):
    b_pages_manager, b_templates_manager = get_pages_access(request.user)
    ret = {}
    file_type = request.POST.get("file_type", None)
    webpage = request.POST.get("webpage", None)
    new_page = request.POST.get("new_page", None)
    if (b_pages_manager or b_templates_manager) and webpage is not None and new_page is not None:
        try:
            if file_type == 'template' and b_templates_manager:
                path = settings.PROJECT_PATH + os.sep + 'skins' + os.sep
            else:
                path = settings.PROJECT_PATH + \
                    os.sep + settings.ZORNA_CONTENT + os.sep
            new_page = slugify(new_page)
            f = new_page + '.html'
            cdir, origin_file = os.path.split(webpage)
            src = path + webpage
            dest = path + cdir + os.sep + f
            if os.path.isfile(dest):
                ret['status'] = 'error'
                ret['message'] = 'A file with the same name already exist'
            else:
                shutil.copyfile(src, dest)
                t = loader.get_template("pages/fm_folder_item.html")
                if cdir:
                    cdir = cdir + '/'
                c = RequestContext(request, {
                                   'cdir': cdir, 'f': new_page, 'file_type': file_type})
                ret['html'] = t.render(c)
                ret['rel'] = "%s%s" % (cdir, f)
                ret['head_html'] = '<li class="%s ext_html"><a href="#" rel="%s%s">%s</a></li>' % (
                    file_type, cdir, f, f)
                ret['status'] = 'success'
                ret['message'] = 'File has been cloned'
        except IOError:
            ret['status'] = 'error'
            ret['message'] = 'Invalid file name'
    else:
        ret['status'] = 'error'
        ret['message'] = 'Access denied'
    return HttpResponse(simplejson.dumps(ret))


def delete_webpage(request):
    b_pages_manager, b_templates_manager = get_pages_access(request.user)
    ret = {}
    if b_pages_manager or b_templates_manager:
        file_type = request.POST.get("file_type", None)
        webpage = request.POST.get("webpage", None)
        try:
            if file_type == 'template' and b_templates_manager:
                path = settings.PROJECT_PATH + os.sep + 'skins' + os.sep
            else:
                path = settings.PROJECT_PATH + \
                    os.sep + settings.ZORNA_CONTENT + os.sep
            src = path + webpage
            os.remove(src)
            ret['status'] = 'success'
            ret['message'] = 'Removed file successfully'
        except IOError:
            ret['status'] = 'error'
            ret['message'] = 'Invalid file name'
    else:
        ret['status'] = 'error'
        ret['message'] = 'Access denied'
    return HttpResponse(simplejson.dumps(ret))


def rename_webpage(request):
    b_pages_manager, b_templates_manager = get_pages_access(request.user)
    ret = {}
    file_type = request.POST.get("file_type", None)
    webpage = request.POST.get("webpage", None)
    new_name = request.POST.get("new_name", None)
    if (b_pages_manager or b_templates_manager) and webpage is not None and new_name is not None:
        try:
            if file_type == 'template' and b_templates_manager:
                path = settings.PROJECT_PATH + os.sep + 'skins' + os.sep
            else:
                path = settings.PROJECT_PATH + \
                    os.sep + settings.ZORNA_CONTENT + os.sep
            src = path + webpage
            head, tail = os.path.split(src)
            new_name = slugify(new_name)
            dest = os.path.join(head, new_name + '.html')
            os.rename(src, dest)
            ret['status'] = 'success'
            ret['message'] = 'File renamed successfully'
        except IOError:
            ret['status'] = 'error'
            ret['message'] = 'Invalid file name'
    else:
        ret['status'] = 'error'
        ret['message'] = 'Access denied'
    return HttpResponse(simplejson.dumps(ret))


def past_webpage(request):
    b_pages_manager, b_templates_manager = get_pages_access(request.user)
    ret = {}
    file_type = request.POST.get("file_type", None)
    webpage = request.POST.get("webpage", None)
    webrel = request.POST.get("webrel", None)
    if (b_pages_manager or b_templates_manager) and webpage is not None and webrel is not None:
        try:
            if file_type == 'template' and b_templates_manager:
                path = settings.PROJECT_PATH + os.sep + 'skins' + os.sep
            else:
                path = settings.PROJECT_PATH + \
                    os.sep + settings.ZORNA_CONTENT + os.sep
            src = path + webpage
            dest = path + webrel
            shutil.move(src, dest)
            head, tail = os.path.split(src)
            t = loader.get_template("pages/fm_folder_item.html")
            c = RequestContext(request, {'cdir': webrel.rstrip(
                '/'), 'f': os.path.splitext(tail)[0], 'file_type': file_type})
            ret['html'] = t.render(c)
            ret['head_html'] = '<li class="%s ext_html"><a href="#" rel="%s%s">%s</a></li>' % (
                file_type, webrel, tail, tail)
            ret['status'] = 'success'
            ret['message'] = 'File pasted successfully'
        except IOError:
            ret['status'] = 'error'
            ret['message'] = 'File error'
    else:
        ret['status'] = 'error'
        ret['message'] = 'Access denied'
    return HttpResponse(simplejson.dumps(ret))


def manage_folder(request):
    b_pages_manager, b_templates_manager = get_pages_access(request.user)
    ret = {}
    file_type = request.POST.get("file_type", None)
    new_folder = request.POST.get("new_folder", None)
    file_rel = request.POST.get("file_rel", None)
    what = request.POST.get("what", 'create')
    if (b_pages_manager or b_templates_manager) and file_rel is not None and new_folder is not None:
        file_rel = normalize_path(file_rel)
        new_folder = slugify(normalize_path(new_folder))
        try:
            if file_type == 'template' and b_templates_manager:
                path = settings.PROJECT_PATH + os.sep + 'skins' + os.sep
            else:
                path = settings.PROJECT_PATH + \
                    os.sep + settings.ZORNA_CONTENT + os.sep

            if what == 'rename':
                c = file_rel.rstrip('/')
                cps = c.split('/')
                cps.pop()
                os.rename(path + file_rel, path + '/'.join(
                    cps) + os.sep + new_folder)
                if cps:
                    dir = '/'.join(cps) + '/'
                else:
                    dir = ''
                ret['url'] = reverse(
                    'fmbrowser_home') + '?file_type=' + file_type + '&dir=' + dir
            else:
                folder = path + file_rel + os.sep + new_folder
                if not os.path.exists(folder):
                    os.mkdir(folder)
                    if file_rel:
                        rel = "%s/%s/" % (file_rel, new_folder)
                    else:
                        rel = "%s/" % new_folder
                    ret['url'] = '<li class="directory collapsed"><a href="#" rel="%s">%s</a></li>' % (
                        rel, new_folder)
                else:
                    ret['url'] = ''

            ret['status'] = 'success'
            ret['message'] = 'Folder created succesfully'
        except IOError:
            ret['status'] = 'error'
            ret['message'] = 'folder management error'
    else:
        ret['status'] = 'error'
        ret['message'] = 'Access denied'
    return HttpResponse(simplejson.dumps(ret))
