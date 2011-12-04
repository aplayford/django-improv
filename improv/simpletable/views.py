from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from simpletable.models import SimpleTable

def render_table(request, id, slug):
    varsContext = {}
    
    table = get_object_or_404(SimpleTable, id=id, active=True)
    if not table.slug == slug:
        return HttpResponseRedirect(table.get_absolute_url())
    
    dynamic_model = table.dataset
    actual_model = dynamic_model.actual
    
    varsContext = {
        'display': table,
        'proxy': dynamic_model,
        'model': actual_model,
        'rows': actual_model.objects.formatted_rows(table.get_formatter())
    }
    
    return render_to_response("simpletable/simpletable.html", varsContext,
                    context_instance=RequestContext(request))