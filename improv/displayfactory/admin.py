from django.contrib import admin

from displayfactory.models import DisplayFormat, NumberFormat, StringFormat

admin.site.register(NumberFormat)
admin.site.register(StringFormat)