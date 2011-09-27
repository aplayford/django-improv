from easyloader.models import EasyLoadCSV
from django.contrib import admin

class DynamicModelAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(EasyLoadCSV)