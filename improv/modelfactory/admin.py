from modelfactory.models import DynamicModel, DynamicField
from modelfactory.forms import EasyLoadTextForm

from django.contrib import admin
from django.conf.urls.defaults import patterns

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

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
            (r'load/', self.load_and_introspect_tsv),
        )
        return my_urls + urls

    def load_and_introspect_tsv(self, request):
        from modelfactory.loaders import Loader

        if request.method == 'POST': # If the form has been submitted...
            form = EasyLoadTextForm(request.POST) # A form bound to the POST data
            if form.is_valid(): # All validation rules pass
                loader = Loader()
                dyn_mod = loader.load_and_introspect_tsv_text(form.cleaned_data['tsv_data'], form.cleaned_data['model_name'], overwrite=True)
                return HttpResponseRedirect(reverse('admin:modelfactory_dynamicmodel_change', args=[dyn_mod.id] )) # Redirect after POST
        else:
            form = EasyLoadTextForm() # An unbound form

        return render_to_response('admin/modelfactory/dynamicmodel/loader.html', {
            'form': form,
        }, context_instance=RequestContext(request))
    
admin.site.register(DynamicModel, DynamicModelAdmin)