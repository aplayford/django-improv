from django.db import models, connection
from django.core.validators import RegexValidator

from south.db import db as southdb

from modelfactory.utils import create_pymodel
from modelfactory.supported_fields import DYN_FIELD_TYPES, DYN_FIELD_DEFAULTS

class DynamicModel(models.Model):
    ############
    ## Fields ##
    ############
    name = models.CharField(max_length=25, unique=True,
                validators=[RegexValidator(r"[\w]+", message="Model name has no spaces.")])
    
    #############
    ## Getters ##
    #############
    @property
    def field_list(self):
        res = {}
        for field in self.fields.all():
            res[field.column_name] = field.pyfield
        return res
    
    @property
    def actual(self):
        """
        Based on this model's name, attached fields and settings, dynamically
        creates an in-memory Model class, which can be queried and manipulated
        like any other Django model.
        """
        
        return create_pymodel(str(self.name), self.field_list,
                              app_label="dynamic_store",
                              module="database.dynamic_store")
    
    ####################################
    ## Database manipulation methods. ##
    ####################################
    
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
        return self.pymodel._meta.db_table in connection.introspection.get_table_list(cursor)
    
    def reset_table(self):
        if self.table_exists():
            self.drop_table()
        return self.create_table()
    
    ##########################
    ## Django model methods ##
    ##########################
    
    def delete(self, *args, **kwargs):
        if self.table_exists():
            self.drop_table()
        return super(DynamicModel, self).delete(*args, **kwargs)
    
    def __unicode__(self):
        return u"%s" % self.name
    
class DynamicField(models.Model):
    model = models.ForeignKey('DynamicModel', related_name="fields")
    column_name = models.CharField(max_length=25)
    field_type = models.CharField(max_length=5, choices=DYN_FIELD_TYPES)
    display_name = models.CharField(max_length=100, blank=True)
    field_settings = models.TextField(max_length=200, blank=True)
    
    @property
    def pyfield(self):
        field_type = self.get_field_type_display()
        
        settings = {}
        settings.update(DYN_FIELD_DEFAULTS[field_type])
        
        if self.field_settings.strip():
            for key, value in [s.split(':= ') for s in self.field_settings.strip().splitlines()]:
                settings[key.strip()] = value.strip()
        
        return getattr(models, field_type)(**settings)
    
    def __unicode__(self):
        return "%s" % self.display_name if self.display_name else self.column_name
    
    class Meta:
        unique_together = ('model', 'column_name',)