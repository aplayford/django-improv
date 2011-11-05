import re

class Introspector(object):
    def __init__(self):
        self.cols = {}
    
    def set_col(self, key, value):
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
    
def introspect_csv(filename, limit=200):
    from csv import DictReader
    
    sniffer = Introspector()
    
    rc = 0
    f = open(filename)
    
    for row in DictReader(f):
        if rc < limit:
            introspect_row(sniffer, row)
            rc += 1
        else:
            break

    f.close()
    
    return sniffer

def introspect_row(sniffer, row):
    for row in DictReader(f):
        for (key, val) in row.items():
            sniffer.set_col(key, val)
            