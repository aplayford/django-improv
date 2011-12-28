from django import forms

class EasyLoadTextForm(forms.Form):
    tsv_data = forms.CharField(widget=forms.widgets.Textarea())
    model_name = forms.SlugField(max_length=50)