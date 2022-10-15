from django import forms

class GeeksForm(forms.Form):
    upload_image = forms.ImageField()