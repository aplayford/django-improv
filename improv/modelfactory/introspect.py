import re
from utils import OrderedDictReader
from collections import OrderedDict

class Introspector(object):
    def __init__(self):
        self.cols = OrderedDict()
        self.col_order = OrderedDict()
    
    def from_stream(self, stream, limit=None):
        for row_count, row in enumerate(OrderedDictReader(stream)):
            if limit is None or row_count < limit:
                self.introspect_row(row)
            else:
                break
        return self
    
    def introspect_row(self, row):
        for (order, (key, val)) in enumerate(row.items()):
            self.set_col(key, val, order)
    
    def ordered_cols(self):
        '''Create a dictionary that brings together cols and col_order.'''
        return dict([(key, (self.cols[key], self.col_order[key])) for key in self.cols.keys()])
    
    def set_col(self, key, value, order):
        if key in self.cols:
            cast = self.cols[key]
        else:
            cast = None
        
        # If we haven't done an initial cast, start at most restrictive and move down.
        if cast == None:
            if self.passes_int(value):
                cast = "INT"
            elif self.passes_float(value):
                cast = "FLOAT"
            elif self.passes_char(value):
                cast = "CHAR"
            else:
                cast = "TEXT"
        # If we've already cast this column, see if the cast can remain.
        elif cast == "INT":
            if self.passes_int(value):
                cast = "INT"
            elif self.passes_float(value):
                cast = "FLOAT"
            elif self.passes_char(value):
                cast = "CHAR"
            else:
                cast = "TEXT"
        elif cast == "FLOAT":
            if self.passes_float(value):
                cast = "FLOAT"
            elif self.passes_char(value):
                cast = "CHAR"
            else:
                cast = "TEXT"
        elif cast == "CHAR":
            if not self.passes_char(value):
                cast = "TEXT"
        else:
            cast = "TEXT"
        
        self.cols[key] = cast
        self.col_order[key] = order
    
    def passes_char(self, value):
        if isinstance(value, basestring):
            if len(value) <= 100:
                return True
        return False
    
    def passes_int(self, value, null=True):
        if re.match('\d{1,3},?\d{,3}?', value):
            value = value.replace(",", "")
        if null and value is None:
            return True
        try:
            return str(int(value)) == str(value)
        except ValueError:
            return False
    
    def passes_float(self, value, null=True):
        if re.match('\d{1,3},?\d{,3}?', value):
            value = value.replace(",", "")
        if null and value is None:
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False