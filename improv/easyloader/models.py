from django.db import models

# Create your models here.
class EasyLoadCSV(models.Model):
    model_name = models.CharField(max_length=50, help_text="No spaces!")   # Need to validate for no spaces
    file = models.FileField(upload_to="data_uploads/easyloader")
    
def post_save_easyload_csv(sender, instance, created, *args, **kwargs):
    from modelfactory.loaders import load_and_introspect_csv
    
    load_and_introspect_csv(instance.file.path, instance.model_name, overwrite=True)
models.signals.post_save.connect(post_save_easyload_csv, sender=EasyLoadCSV)