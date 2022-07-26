from django import forms

class PostForm(forms.Form):
    title = forms.CharField(max_length=255)
    content = forms.CharField()
    cover = forms.ImageField(required=False)
    date = forms.DateField(required=False)
    category = forms.CharField(required=False)
    permanent = forms.CharField(max_length=255)


class PostTranslateForm(forms.Form):
    title = forms.CharField(max_length=255)
    content = forms.CharField()
