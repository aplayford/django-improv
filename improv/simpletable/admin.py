from django.contrib import admin
from simpletable.models import SimpleTable, SimpleColumn

class SimpleColumnInline(admin.TabularInline):
    exclude = ('field',)
    extra = 0
    model = SimpleColumn

class SimpleTableAdmin(admin.ModelAdmin):
    exclude = ('content_type',)
    inlines = [SimpleColumnInline]

admin.site.register(SimpleTable, SimpleTableAdmin)