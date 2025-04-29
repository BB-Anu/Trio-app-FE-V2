from django import forms
from ckeditor.widgets import CKEditorWidget

class TemplateForm(forms.Form):
    name = forms.CharField( required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    content = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))

class TemplateDocumentForm(forms.Form):
    Template=forms.IntegerField(required=False,widget=forms.NumberInput(attrs={"class":"form-control"}))
    content = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
