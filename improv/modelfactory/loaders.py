from modelfactory.introspect import introspect_csv
from modelfactory.models import DynamicModel, DynamicField
from django.template.defaultfilters import slugify

import codecs
from csv import DictReader

## TODOs:
## 1) Fix error that would come if two fieldify() fields created an overlap.
## 2) Handle unicode correctly. Errors="ignore" is a *really* bad solution.

def fieldify(txt):
    return slugify(txt).replace('-', '_')

class Cast(object):
    def __init__(self, type):
        self.type = type
    
    def clean(self, v):
        try:
            return getattr(self, self.type.lower())(v)
        except AttributeError:
            return v
    
    def float(self, v):
        return v.replace(",", "")
    
    def int(self, v):
        return v.replace(",", "")
    
    def char(self, v):
        return unicode(v, errors="ignore")

def load_and_introspect_csv(filename, model_name, repl={}, overwrite=True):
    sniffed = introspect_csv(filename)

    if overwrite:
        try:
            DynamicModel.objects.get(name=model_name).delete()
        except DynamicModel.DoesNotExist:
            pass
    
    model = DynamicModel(name=model_name)
    model.save()
    
    fields = {}
    for (field, field_data) in sniffed.ordered_cols().items():
        try:
            key = repl[field]
        except KeyError:
            key = field
        
        # Cache these values here, speed up things later.
        fields[key] = {}
        fields[key]['key'] = fieldify(field)
        fields[key]['cast'] = Cast(type)
        
        model.fields.create(column_name=fields[key]['key'], display_name=key, field_type=field_data[0], field_order=field_data[1])
    
    model.create_table()
    
    load_csv(model, filename, fields, repl)

def load_csv(model, filename, fields, repl={}):
    f = codecs.open(filename)
    
    for row in DictReader(f):
        load_row(model, row, fields, repl)
    
    f.close()
    
def load_row(model, row, fields, repl={}):
    obj = model.actual()
    
    for (key, val) in row.items():
        if key in repl:
            key = repl[key]
        
        cast = fields[key]['cast']
        field = fields[key]['key']
        
        setattr(obj, field, cast.clean(val))
    
    obj.save()
    
    return obj