from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

___all__ = ('CharModel', 'IntegerModel', 'TextModel', 'BooleanModel'
            'DateModel', 'DateTimeModel', 'ForeignKeyModel', 'ManyToManyModel',
            'FileModel', 'TestModel',)


class CharModel(models.Model):
    field = models.CharField(max_length=10)


class ForeignKeyModel(models.Model):
    field = models.ForeignKey(CharModel)


class ManyToManyModel(models.Model):
    field = models.ManyToManyField(CharModel)


class FileModel(models.Model):
    field = models.FileField(upload_to='.')
