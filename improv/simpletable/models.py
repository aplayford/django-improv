from django.db import models
from displayfactory.models import DisplayBase

class SimpleTable(DisplayBase):
    page_title = models.CharField(max_length=100, blank=True)
    leadin = models.TextField(blank=True)

    view_name = "simpletable_view"

    def save(self, *args, **kwargs):
    	res = super(SimpleTable, self).save(*args, **kwargs)

    	for field in self.dataset.fields.all():
    		self.columns.get_or_create(field=field)
    	
    	return res

class SimpleColumn(models.Model):
	table = models.ForeignKey('SimpleTable', related_name="columns")
	field = models.ForeignKey('modelfactory.DynamicField')
	show = models.BooleanField()

	def __unicode__(self):
		return unicode(self.field)

	class Meta:
		unique_together = ('table', 'field',)