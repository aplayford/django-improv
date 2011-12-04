from modelfactory.models import DynamicModel, DynamicField
from modelfactory.forms import EasyLoadFileForm, EasyLoadTextForm

from django.contrib import admin
from django.conf.urls.defaults import patterns

from django.shortcuts import render_to_response
from django.template import RequestContext

class DynamicFieldInline(admin.StackedInline):
    model = DynamicField
    extra = 0

class DynamicModelAdmin(admin.ModelAdmin):
    inlines = [DynamicFieldInline]

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super(DynamicModelAdmin, self).get_urls()
        my_urls = patterns('',
            (r'load/csv/', self.load_and_introspect),
        )
        return my_urls + urls

    def load_and_introspect(self, request):
        from modelfactory.loaders import load_and_introspect_tsv

        if request.method == 'POST': # If the form has been submitted...
            form = EasyLoadTextForm(request.POST) # A form bound to the POST data
            if form.is_valid(): # All validation rules pass
                try:
                    dyn_mod = load_and_introspect_tsv(form.cleaned_data['tsv_data'], form.cleaned_data['model_name'], overwrite=True)
                    return HttpResponseRedirect('/thanks/') # Redirect after POST
                except:
                    pass
        else:
            form = EasyLoadTextForm() # An unbound form

        return render_to_response('admin/modelfactory/dynamicmodel/loader.html', {
            'form': form,
        }, context_instance=RequestContext(request))

        load_and_introspect_csv(instance.file.path, instance.model_name, overwrite=True)
    
admin.site.register(DynamicModel, DynamicModelAdmin)