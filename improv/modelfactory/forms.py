from django import forms

class EasyLoadFileForm(forms.Form):
    csv_file = forms.FileField()
    model_name = forms.SlugField(max_length=50)

class EasyLoadTextForm(forms.Form):
    tsv_data = forms.CharField(widget=forms.widgets.Textarea())
    model_name = forms.SlugField(max_length=50)