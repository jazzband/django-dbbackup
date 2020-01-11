from __future__ import unicode_literals
from django.db import models

___all__ = ('CharModel', 'IntegerModel', 'TextModel', 'BooleanModel'
            'DateModel', 'DateTimeModel', 'ForeignKeyModel', 'ManyToManyModel',
            'FileModel', 'TestModel',)


class CharModel(models.Model):
    field = models.CharField(max_length=10)


class ForeignKeyModel(models.Model):
    field = models.ForeignKey(CharModel, on_delete=models.CASCADE)


class ManyToManyModel(models.Model):
    field = models.ManyToManyField(CharModel)


class FileModel(models.Model):
    field = models.FileField(upload_to='.')
