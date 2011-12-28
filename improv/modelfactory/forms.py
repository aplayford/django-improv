from django import forms

class EasyLoadTextForm(forms.Form):
    model_name = forms.SlugField(max_length=50)
    tsv_data = forms.CharField(widget=forms.widgets.Textarea())