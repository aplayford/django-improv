from modelfactory.introspect import Introspector
from modelfactory.models import DynamicModel, DynamicField
from django.template.defaultfilters import slugify

import codecs
from io import StringIO
from utils import OrderedDictReader

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

class Loader(object):
    def __init__(self, model=None):
        self.model = model
        self.streamer = None
        self.fields = {}
    def __del__(self):
        if hasattr(self, "fileobj"):
            self.fileobj.close()
    
    def assign_model(self, model):
        self.model = model
        return self.model
    
    ####################
    ## Stream methods ##
    ####################
    
    def open_file_stream(self, filename):
        self.streamer = "fileobj"
        self.fileobj = codecs.open(filename)
        return self.fileobj
        
    def open_text_stream(self, text):
        self.streamer = "textio"
        self.textio = StringIO(unicode(text))
        return self.textio
    
    def get_stream(self):
        return getattr(self, self.streamer)
    
    def reset_stream(self):
        io = getattr(self, self.streamer)
        io.seek(0)
        return setattr(self, self.streamer, io)
    
    ###################
    ## Introspection ##
    ###################
    
    def introspect_stream(self, model_name, repl=None, reader_settings=None, overwrite=False):
        sniffed = Introspector().from_stream(self.get_stream())
        self.reset_stream()
        
        if repl is None:
            repl = {}
        if reader_settings is None:
            reader_settings = {}
    
        if overwrite:
            try:
                DynamicModel.objects.get(name=model_name).delete()
            except DynamicModel.DoesNotExist:
                pass
        
        model = DynamicModel(name=model_name)
        model.save()
        self.assign_model(model)
        
        used_fields = set()
        
        for (field, field_data) in sniffed.ordered_cols().items():
            try:
                key = repl[field]
            except KeyError:
                key = field
            
            # Cache these values here, speed up things later.
            fieldname = fieldify(field)
            if fieldname in used_fields:
                ct = 1
                while fieldname in used_fields:
                    fieldname = u"%s%s" % (fieldname, ct)
                    ct += 1
            used_fields.add(fieldname)
            
            self.fields[key] = {}
            self.fields[key]['key'] = fieldname
            self.fields[key]['cast'] = Cast(field_data[0])
            
            model.fields.create(column_name=self.fields[key]['key'], display_name=key, field_type=field_data[0], field_order=field_data[1])
        
        model.create_table()
    
    #############
    ## Loading ##
    #############
    
    def load_stream(self, reader_settings=None, **kwargs):
        if reader_settings is None:
            reader_settings = {}
        for row in OrderedDictReader(self.get_stream(), **reader_settings):
            self.load_row(row, **kwargs)
    
    def load_row(self, row, repl=None):
        if self.model is None:
            raise ValueError()
            
        obj = self.model.actual()
        
        if repl is None:
            repl = {}
        
        for (key, val) in row.items():
            if key in repl:
                key = repl[key]
            
            cast = self.fields[key]['cast']
            field = self.fields[key]['key']
            
            setattr(obj, field, cast.clean(val))
        
        obj.save()
        
        return obj
        
    ############
    ## cutoff ##
    ############
    def load_and_introspect_csv(self, filename, model_name, repl=None, reader_settings=None, overwrite=True):
        self.open_file_stream(filename)
        self.introspect_stream(model_name, reader_settings=reader_settings, overwrite=overwrite)
        self.load_stream(repl)
    
    def load_and_introspect_tsv_text(self, filename, model_name, repl=None, reader_settings=None, overwrite=True):
        from csv import excel_tab
        
        if reader_settings is None:
            reader_settings = {}
        reader_settings['dialect'] = excel_tab
        
        self.open_file_stream(filename)
        self.introspect_stream(model_name, reader_settings=reader_settings, overwrite=overwrite)
        self.load_stream(repl)