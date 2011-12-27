from django.db import models, connection
from django.core.validators import RegexValidator

from collections import OrderedDict

from south.db import db as southdb

from modelfactory.supported_fields import DYN_FIELD_TYPES, DYN_FIELD_DEFAULTS

###################
## Actual models ##
###################

class DynamicModel(models.Model):
    ############
    ## Fields ##
    ############
    name = models.CharField(max_length=25, unique=True,
                validators=[RegexValidator(r"[\w]+", message="Model name has no spaces.")])
    
    #############
    ## Getters ##
    #############
    def fields_actual(self):
        res = OrderedDict()
        for field in self.fields.all():
            res[field.column_name] = field.dynamic_field
        return res
    
    @property
    def actual(self):
        """
        Based on this model's name, attached fields and settings, dynamically
        creates an in-memory Model class, which can be queried and manipulated
        like any other Django model.
        """
        
        dynamic = {
            'dynamic_fields': OrderedDict([(f.column_name, f) for f in self.fields.all()])
        }
        
        return instance_dynamic_model(
            str(self.name),
            self.fields_actual(),
            "dynamic_store",
            "database.dynamic_store",
            dynamic,
        )
    
    ###########################
    ## Database manipulation ##
    ###########################
    
    def create_table(self):
        model = self.actual
        
        fields = []
        for field in model._meta.fields:
            fields.append((field.name, field,))
        
        return southdb.create_table(model._meta.db_table, fields)
    
    def drop_table(self):
        model = self.actual
        return southdb.delete_table(model._meta.db_table, cascade=True)
    
    def table_exists(self):
        cursor = connection.cursor()
        return self.actual._meta.db_table in connection.introspection.get_table_list(cursor)
    
    def reset_table(self):
        if self.table_exists():
            self.drop_table()
        return self.create_table()
    
    ############################
    ## Django model overrides ##
    ############################
    
    def delete(self, *args, **kwargs):
        if self.table_exists():
            self.drop_table()
        return super(DynamicModel, self).delete(*args, **kwargs)
    
    def __unicode__(self):
        return u"%s" % self.name
    
class DynamicField(models.Model):
    model = models.ForeignKey('DynamicModel', related_name="fields")
    column_name = models.CharField(max_length=50)
    field_type = models.CharField(max_length=5, choices=DYN_FIELD_TYPES)
    display_name = models.CharField(max_length=100, blank=True)
    field_settings = models.TextField(max_length=200, blank=True)
    field_order = models.PositiveIntegerField()
    
    @property
    def dynamic_field(self):
        field_type = self.get_field_type_display()
        
        settings = {}
        settings.update(DYN_FIELD_DEFAULTS[field_type])
        
        if self.field_settings.strip():
            for key, value in [s.split(':= ') for s in self.field_settings.strip().splitlines()]:
                settings[key.strip()] = value.strip()
        
        return getattr(models, field_type)(**settings)
    
    def __unicode__(self):
        return u"%s" % self.display_name if self.display_name else self.column_name
    
    class Meta:
        unique_together = ('model', 'column_name',)
        ordering = ('field_order',)
        unique_together = (('model', 'column_name',), ('model', 'field_order'),)


###########################
## Dynamic model support ##
###########################

class DynamicModelManager(models.Manager):
    def formatted_rows(self, formatter, exclude=None):
        if not exclude:
            exclude = []
        
        for row in self.iterator():
            rowdata = OrderedDict()
            for key, field in self.model.Dynamic['dynamic_fields'].items():
                if not key in exclude:
                    rowdata[key] = formatter.wrap_value(field, getattr(row, key))
            yield rowdata
            

class DynamicModelBase(models.Model):
    """
    All dynamically created models inherit from this.
    """
    objects = DynamicModelManager()
    
    def __unicode__(self):
        if hasattr(self, "magic_box"):
            return getattr(self, self.magic_box['unicode_val'])
        return u"unnamed object"
    
    class Meta:
        abstract = True

def instance_dynamic_model(name, fields, app_label, module, dynamic_data=None, options=None, admin_options=None):
    """
    Using metadata that describes a model, instance it in-memory.
    
    Code based on http://code.djangoproject.com/wiki/DynamicModels.
    """
    class Meta:
        pass # Using type('Meta', ...) gives a dictproxy error during model creation
    setattr(Meta, 'app_label', app_label)
    
    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.iteritems():
            setattr(Meta, key, value)
    
    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta': Meta, 'Dynamic': dynamic_data}
    attrs.update(fields) # Add fields
    
    # Create the class, which automatically triggers ModelBase processing
    model = type(name, (DynamicModelBase,), attrs)
    
    # Create an Admin class if admin options were provided
    if admin_options is not None:
        class Admin(admin.ModelAdmin):
            pass
        for key, value in admin_options:
            setattr(Admin, key, value)
        admin.site.register(model, Admin)
    
    return model
