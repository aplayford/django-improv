from django.contrib import admin
from simpletable.models import SimpleTable, SimpleColumn

class SimpleColumnInline(admin.StackedInline):
	exclude = ('field',)
	extra = 0
	model = SimpleColumn

class SimpleTableAdmin(admin.ModelAdmin):
	inlines = [SimpleColumnInline]

admin.site.register(SimpleTable, SimpleTableAdmin)