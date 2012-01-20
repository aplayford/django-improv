# Django Library
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.views.generic import DetailView

# Local Library
from simpletable.models import SimpleTable


class RenderTable(DetailView):
    
    context_object_name = 'simpletable/simpletable.html'
    context_name = 'display'
    
    def get_queryset(self):
        self.table = get_object_or_404(SimpleTable, 
                                    id = self.kwargs['id'], 
                                    active=True)
        return self.table
        
    def get_context_data(self, **kwargs):
        context = super(RenderTable, self).get_contet_data(**kwargs)
        
        dynamic_model = self.table.dataset
        actual_model = dynamic_model.actual
        
        context['display'] = actual_model

        context['rows'] = actual_model.objects.\
                            formatted_rows(self.table.get_formatter(), 
                            exclude=[f.field.column_name for f in self.table.fields.all() if not f.show])
        return context
        
# def render_table(request, id, slug):
#     varsContext = {}
#     
#     table = get_object_or_404(SimpleTable, id=id, active=True)
#     if not table.slug == slug:
#         return HttpResponseRedirect(table.get_absolute_url())
#     
#     dynamic_model = table.dataset
#     actual_model = dynamic_model.actual
#     
#     varsContext = {
#         'display': table,
#         'model': actual_model,
#         'rows': actual_model.objects.formatted_rows(table.get_formatter(), exclude=[f.field.column_name for f in table.fields.all() if not f.show])
#     }
#     
#     return render_to_response("simpletable/simpletable.html", varsContext,
#                     context_instance=RequestContext(request))