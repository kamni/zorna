from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django import forms
from mptt.forms import TreeNodeChoiceField
from zorna.notes.models import ZornaNote, ZornaNoteCategory, ZornaNoteFile
from ckeditor.widgets import CKEditorWidget

from zorna.site.models import SiteOptions

class ZornaNoteForm(ModelForm):
    category = TreeNodeChoiceField(queryset=ZornaNoteCategory.tree.filter())
    title = forms.CharField(label=_(
        u'Title'), widget=forms.TextInput(attrs={'size': '80'}))
    content = forms.CharField(_(u'body'), widget=forms.Textarea(
        attrs={'rows': '5', 'cols': '80'}))

    class Meta:
        model = ZornaNote

    def __init__(self, request, *args, **kwargs):
        super(ZornaNoteForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = ZornaNoteCategory.tree.filter(
            owner=request.user)
        self.fields['content'] = forms.CharField(label=_(u'body'), 
            widget=CKEditorWidget(config_name=SiteOptions.objects.get_ckeditor_config(request)))


class ZornaNoteCategoryForm(ModelForm):
    parent = TreeNodeChoiceField(
        queryset=ZornaNoteCategory.tree.filter(), required=False, empty_label="-- Nothing --")

    class Meta:
        model = ZornaNoteCategory

    def __init__(self, request, *args, **kwargs):
        super(ZornaNoteCategoryForm, self).__init__(*args, **kwargs)
        self.fields['parent'].queryset = ZornaNoteCategory.tree.filter(
            owner=request.user)


class ZornaNoteFileForm(ModelForm):
    file = forms.CharField(label=_(
        u'Attachment'), widget=forms.FileInput(attrs={'size': '80'}))
    description = forms.CharField(label=_(
        u'Description'), widget=forms.TextInput(attrs={'size': '80'}))

    class Meta:
        model = ZornaNoteFile
