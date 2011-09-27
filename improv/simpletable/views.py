from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext
from simpletable.models import SimpleTable

def render_table(request, slug):
    varsContext = {}
    
    table = get_object_or_404(SimpleTable, slug=slug, active=True)
    dynamic_model = table.dataset
    actual_model = dynamic_model.pymodel
    
    varsContext = {
        'display': table,
        'proxy': dynamic_model,
        'model': actual_model,
        'rows': actual_model.objects.row_iterator()
    }
    
    return render_to_response("simpletable/simpletable.html", varsContext,
                    context_instance=RequestContext(request))