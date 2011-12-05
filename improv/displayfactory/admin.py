from django.contrib import admin

from displayfactory.models import DisplayFormat, NumberFormat, StringFormat

class NumberFormatAdmin(admin.ModelAdmin):
    exclude = ('content_type',)
class StringFormatAdmin(admin.ModelAdmin):
    exclude = ('content_type',)

admin.site.register(NumberFormat, NumberFormatAdmin)
admin.site.register(StringFormat, StringFormatAdmin)