from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

#############
## Helpers ##
#############

class Formatter(object):
    def __init__(self, display):
        self.display = display
        self.fields = dict([(f.field, f,) for f in display.fields.all()])
    
    def wrap_value(self, field, val):
        class DisplayNode(object):
            def __init__(self, display, fields, field, val):
                self.display = display
                self.field = field
                try:
                    self.display_field = fields[field]
                except ObjectDoesNotExist:
                    self.display_field = None
                self.val = val
            
            @property
            def render(self):
                if self.display_field and self.display_field.formatter:
                    return self.display_field.formatter.render(self.val)
                return self.val
            
            def __str__(self):
                return self.__unicode__(self)
            def __unicode__(self):
                return self.render
                
        return DisplayNode(self.display, self.fields, field, val)

class ActualSelfAwareModel(models.Model):
    content_type = models.ForeignKey(ContentType, blank=True)
    actual_self = generic.GenericForeignKey('content_type', 'id')
    
    def save(self, *args, **kwargs):
        print("test")
        self.content_type = ContentType.objects.get_for_model(self.__class__)
        super(ActualSelfAwareModel, self).save(*args, **kwargs)
        
    class Meta:
        abstract = True


#################
## DisplayBase ##
#################

class DisplayPackager(models.Model):
    pass
    
class DisplayBase(ActualSelfAwareModel):
    dataset = models.ForeignKey('modelfactory.DynamicModel')
    active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    packager = models.ForeignKey('DisplayPackager', blank=True, null=True)
    
    @models.permalink
    def get_absolute_url(self):
        view_name = self.content_type.model_class().view_name
        return (view_name, [], {'id': self.id, 'slug': self.slug})
    
    def get_formatter(self):
        return Formatter(self)

class DisplayField(models.Model):
    formatter = models.ForeignKey('DisplayFormat', blank=True, null=True)
    label = models.CharField(max_length=50, blank=True)
    field = models.ForeignKey('modelfactory.DynamicField')
    
    class Meta:
        abstract = True


#######################
## DisplayFormatters ##
#######################

class DisplayFormat(ActualSelfAwareModel):
    #field = models.ForeignKey('modelfactory.DynamicField', related_name="displayformats")
    name = models.CharField(max_length=50)
    
    def render(self, value):
        if self.actual_self:
            return self.actual_self.render(value)
        return value
    
    def __unicode__(self):
        return self.name

class NumberFormat(DisplayFormat):
    add_commas = models.BooleanField()
    decimal_places = models.PositiveIntegerField(default=0)
    preprint = models.CharField(max_length=50, blank=True)
    postprint = models.CharField(max_length=50, blank=True)
    
    def render(self, value):
        decimal_places = self.decimal_places if self.decimal_places else 0
        if self.add_commas:
            value = ("{:,.%if}" % decimal_places).format(value)
        r = "%s%s%s" % (self.preprint, value, self.postprint)
        return r

class StringFormat(DisplayFormat):
    trim_to = models.IntegerField(blank=True)
    trim_by = models.CharField(max_length=3, choices = (
        ('WR', 'Words'), ('CH', 'Characters'))
    )
    capitalize = models.CharField(max_length=5, choices = (
        ('--', 'No changes'),
        ('up', 'UPPERCASE'),
        ('down', 'lowercase'),
        ('title', 'Title Case'),
        ('cap1', 'Cap first'),
    ))