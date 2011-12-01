from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

class DisplayPackager(models.Model):
    pass
    
class DisplayBase(models.Model):
    dataset = models.ForeignKey('modelfactory.DynamicModel')
    active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=50, unique=True)

    packager = models.ForeignKey('DisplayPackager', blank=True, null=True)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)

    @models.permalink
    def get_absolute_url(self):
        view_name = self.content_type.model_class().view_name
        return (view_name, [], {'slug': self.slug})

    def save(self, *args, **kwargs):
        if self.content_type is None:
            ct = ContentType.objects.get_for_model(self.__class__)
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        super(DisplayBase, self).save(*args, **kwargs)


class DisplayFormat(models.Model):
    display = models.ForeignKey('DisplayBase')
    field = models.ForeignKey('modelfactory.DynamicField', related_name="displayformats")
    content_type = models.ForeignKey(ContentType)
    actual_self = generic.GenericForeignKey('content_type', 'id')

    class Meta:
        unique_together = ('display', 'field')

class NumberFormat(DisplayFormat):
    add_commas = models.BooleanField()
    decimal_places = models.BooleanField()
    preprint = models.CharField(max_length=50, blank=True)
    postprint = models.CharField(max_length=50, blank=True)

class StringFormat(DisplayFormat):
    trim_to = models.IntegerField(blank=True)
    trim_by = models.CharField(max_length=3, choices = (
        ('WR', 'Words'), ('CH', 'Characters'))
    )
    capitalize = models.CharField(max_length=5, choices = (
        ('--', 'No changes'),
        ('up', 'UPPERCASE'),
        ('down', 'lowercase'),
        ('title', 'Title Case'),
        ('cap1', 'Cap first'),
    ))