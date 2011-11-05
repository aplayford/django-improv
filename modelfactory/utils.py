from django.db import models

class DynamicModelManager(models.Manager):
    def row_iterator(self, exclude=[]):
        for row in self.iterator():
            rowdata = {}
            for val in self.model._meta.fields:
                if not val in exclude:
                    rowname = val.name
                    rowdata[rowname] = getattr(row, rowname)
            yield rowdata

class DynamicModelBase(models.Model):
    objects = DynamicModelManager()
    
    class Meta:
        abstract = True

def create_pymodel(name, fields=None, app_label='', module='', options=None, admin_opts=None):
    """
    Create Python class version of a model in memory. Code based on
    http://code.djangoproject.com/wiki/DynamicModels.
    """
    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        pass
    
    if app_label:
        # app_label must be set using the Meta inner class
        setattr(Meta, 'app_label', app_label)
    
    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.iteritems():
            setattr(Meta, key, value)
    
    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta': Meta}
    
    # Add in any fields that were provided
    if fields:
        attrs.update(fields)
    
    # Create the class, which automatically triggers ModelBase processing
    model = type(name, (DynamicModelBase,), attrs)
    
    # Create an Admin class if admin options were provided
    #if admin_opts is not None:
    #    class Admin(admin.ModelAdmin):
    #        pass
    #    for key, value in admin_opts:
    #        setattr(Admin, key, value)
    #    admin.site.register(model, Admin)
    
    return model