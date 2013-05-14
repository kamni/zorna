import os
from django.forms import ModelForm
from django.template.defaultfilters import slugify
from django import forms
from django.utils.translation import ugettext_lazy as _
from ckeditor.widgets import CKEditorWidget


from zorna.articles.models import ArticleCategory, ArticleAttachments, ArticleStory, ArticleComments

from mptt.forms import TreeNodeChoiceField


class ArticleCategoryForm(ModelForm):
    parent = TreeNodeChoiceField(queryset=ArticleCategory.tree.filter(), required = False, empty_label="-- Nothing --")
    template = forms.CharField(widget=forms.Textarea(attrs={'rows':'10', 'cols':'80'}), required=False)
    
    class Meta:
        model = ArticleCategory

    def clean_slug(self):
        if 'slug' in self.cleaned_data and 'name' in self.cleaned_data:
            if self.cleaned_data['slug'] != '':
                pass
            else:
                self.cleaned_data['slug'] = self.cleaned_data['name']
            self.cleaned_data['slug'] = slugify(self.cleaned_data['slug'])        
            return self.cleaned_data['slug']
        else:
            raise forms.ValidationError(_(u'You must provide a slug or a category name'))

class ArticleAttachmentsForm(ModelForm):
    attached_file = forms.CharField(label=_(u'Attachment'), widget=forms.FileInput(attrs={'size':'80'}))
    description = forms.CharField(label=_(u'Description'), widget=forms.TextInput(attrs={'size':'80'}))

    class Meta:
        model = ArticleAttachments
        
class ArticleStoryForm(ModelForm):
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'size':'80'}))
    title = forms.CharField(label=_(u'title'), widget=forms.TextInput(attrs={'size':'80'}))
    slug = forms.SlugField(label=_(u'slug'), widget=forms.TextInput(attrs={'size':'80'}), required=False)
    head = forms.CharField(label=_(u'head'), widget=forms.Textarea(attrs={'rows':'5', 'cols':'80'}), required=False)
    body = forms.CharField(label=_(u'body'), widget=CKEditorWidget())

    class Meta:
        model = ArticleStory
        
    def clean_image(self):
        data = self.cleaned_data['image']
        if data:
            (root, ext) = os.path.splitext(data.name.lower())
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                _(u"%(ext)s is an invalid file extension. Authorized extensions are : %(valid_exts_list)s") % 
                { 'ext' : ext, 'valid_exts_list' : ", ".join(allowed_extensions) })
        return data
    
    def clean_slug(self):
        if 'slug' in self.cleaned_data and 'title' in self.cleaned_data:
            if self.cleaned_data['slug'] != '':
                pass
            else:
                self.cleaned_data['slug'] = self.cleaned_data['title']
            self.cleaned_data['slug'] = slugify(self.cleaned_data['slug'])        
            return self.cleaned_data['slug']
        else:
            raise forms.ValidationError(_(u'You must provide a slug or a story title'))    
        
class ArticleCommentsForm(ModelForm):

    class Meta:
        model = ArticleComments
