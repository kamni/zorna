import os
from django.conf import settings
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.template.defaultfilters import slugify
from mptt.forms import TreeNodeChoiceField

from zorna.articles.models import ArticleCategory
from zorna.faq.models import Faq
from zorna.forms.models import FormsForm, FormsWorkspace
from zorna.menus.models import ZornaMenuItem


class ZornaMenuItemBaseForm(ModelForm):
    parent = TreeNodeChoiceField(
        queryset=ZornaMenuItem.tree.filter(), required=False, empty_label="-- Nothing --")

    class Meta:
        model = ZornaMenuItem

    def clean_slug(self):
        if 'slug' in self.cleaned_data and 'name' in self.cleaned_data:
            if self.cleaned_data['slug'] != '':
                pass
            else:
                self.cleaned_data['slug'] = self.cleaned_data['name']
            self.cleaned_data['slug'] = slugify(self.cleaned_data['slug'])
            return self.cleaned_data['slug']
        else:
            raise forms.ValidationError(_(
                u'You must provide a slug or a menu item name'))


class ZornaMenuItemContainerForm(ZornaMenuItemBaseForm):
    pass


class ZornaMenuItemUrlForm(ZornaMenuItemBaseForm):
    url = forms.CharField(widget=forms.TextInput(attrs={
                          'size': 80}), label=_(u'Url'), required=False)


class ZornaMenuItemArticleCategoryForm(ZornaMenuItemBaseForm):
    category = TreeNodeChoiceField(
        queryset=ArticleCategory.tree.filter(), required=True)


class ZornaMenuItemFaqForm(ZornaMenuItemBaseForm):
    faq = forms.ModelChoiceField(queryset=Faq.objects.all(), required=True)


class ZornaMenuItemPageContentForm(ZornaMenuItemBaseForm):
    page = forms.ChoiceField(required=True)

    def __init__(self, *args, **kwargs):
        super(ZornaMenuItemPageContentForm, self).__init__(*args, **kwargs)
        self.fields['page'].choices = self.pages_as_choices()

    def pages_as_choices(self, path=''):
        root_path = settings.PROJECT_PATH + \
            os.sep + settings.ZORNA_CONTENT + os.sep
        len_root_path = len(root_path)
        pages = []
        for root, dirs, files in os.walk(root_path):
            for f in files:
                fpath = os.path.join(root, f).replace('\\', '/')
                fpath = os.path.splitext(fpath)[0]
                pages.append(('/content/' + fpath[
                             len_root_path:], fpath[len_root_path:]))
        if not path:
            path = settings.PROJECT_PATH + \
                os.sep + settings.ZORNA_CONTENT + os.sep
        return pages


class ZornaMenuItemFormsForm(ZornaMenuItemBaseForm):
    form = forms.ModelChoiceField(
        queryset=FormsForm.objects.all(), required=True)

    def __init__(self, *args, **kwargs):
        super(ZornaMenuItemFormsForm, self).__init__(*args, **kwargs)
        self.fields['form'].choices = self.forms_as_choices()

    def forms_as_choices(self):
        forms = []
        for wp in FormsWorkspace.objects.all():
            new_form = []
            sub_forms = []
            for form in wp.formsform_set.all():
                sub_forms.append([form.pk, form.name])

            new_form = [wp.name, sub_forms]
            forms.append(new_form)

        return forms
