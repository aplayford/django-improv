from django.db import models
from displayfactory.models import DisplayBase, DisplayField

class SimpleTable(DisplayBase):
    page_title = models.CharField(max_length=100, blank=True)
    leadin = models.TextField(blank=True)

    view_name = "simpletable_view"

    def save(self, *args, **kwargs):
        res = super(SimpleTable, self).save(*args, **kwargs)
        for field in self.dataset.fields.all():
            self.fields.get_or_create(field=field, order=field.field_order)
        return res
    
    def __unicode__(self):
        return u"%s" % self.dataset

class SimpleColumn(DisplayField):
    table = models.ForeignKey('SimpleTable', related_name="fields")
    order = models.PositiveIntegerField()
    show = models.BooleanField(default=True)

    class Meta:
        unique_together = ('table', 'field',)
        ordering = ('table', 'order',)