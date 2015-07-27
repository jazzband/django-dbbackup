"""
Lazy storage adapted to Django buit-in one.
"""
from django.core.files.storage import get_storage_class
from .base import BaseStorage
from .. import settings


class Storage(BaseStorage):
    def __init__(self, storage_path=None, **options):
        storage_path = storage_path or settings.BUILTIN_STORAGE
        options = options.copy()
        options.update(settings.STORAGE_OPTIONS)
        self.storageCls = get_storage_class(storage_path)
        self.storage = self.storageCls(**options)
        self.name = self.storageCls.__name__
        self.backup_dir = self.name

    def delete_file(self, filepath):
        self.storage.delete(name=filepath)

    def list_directory(self):
        return self.storage.listdir(path='')[1]

    def write_file(self, filehandle, filename):
        self.storage.save(name=filename, content=filehandle)

    def read_file(self, filepath):
        return self.storage.open(name=filepath, mode='rb')
