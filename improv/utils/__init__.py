from csv import DictReader
from collections import OrderedDict

def utfify(stream):
    '''Convert a stream into utf-8.'''
    for l in stream:
        yield l.encode('utf-8')

def deutfify(stream):
    '''Convert a stream out of utf-8.'''
    for l in stream:
        yield l.decode('utf-8')


class OrderedDictReader(DictReader):
    '''
    A quick rip of csv.DictReader to replace dict with OrderedDict. For now, code is mostly
    borrowed from Python core.
    '''
    def __init__(self, *args, **kwargs):
        
        args = list(args)
        args[0] = utfify(args[0])
        
        DictReader.__init__(self, *args, **kwargs) #  DictReader is apparently an old-style  class
    
    def next(self):
        if self.line_num == 0:
            # Used only for its side effect.
            self.fieldnames
        row = self.reader.next()
        self.line_num = self.reader.line_num

        # unlike the basic reader, we prefer not to return blanks,
        # because we will typically wind up with a dict full of None
        # values
        while row == []:
            row = self.reader.next()
        d = OrderedDict(zip(self.fieldnames, deutfify(row)))
        lf = len(self.fieldnames)
        lr = len(row)
        if lf < lr:
            d[self.restkey] = row[lf:]
        elif lf > lr:
            for key in self.fieldnames[lr:]:
                d[key] = self.restval
        return d