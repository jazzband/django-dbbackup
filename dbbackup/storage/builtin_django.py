"""
Wrapper around Django storage API.
"""
from django.core.files.storage import get_storage_class
from .base import BaseStorage
from .. import settings


class Storage(BaseStorage):
    def __init__(self, storage_path=None, **options):
        """
        Initialize a Django Storage instance with given options.

        :param storage_path: Path to a Django Storage class with dot style
                             If ``None``, ``settings.DBBACKUP_BUILTIN_STORAGE``
                             will be used.
        :type storage_path: str
        """
        storage_path = storage_path or settings.BUILTIN_STORAGE
        options = options.copy()
        options.update(settings.STORAGE_OPTIONS)
        self.storageCls = get_storage_class(storage_path)
        self.storage = self.storageCls(**options)
        self.name = self.storageCls.__name__

    def delete_file(self, filepath):
        self.storage.delete(name=filepath)

    def list_directory(self):
        return self.storage.listdir('')[1]

    def write_file(self, filehandle, filename):
        self.storage.save(name=filename, content=filehandle)

    def read_file(self, filepath):
        return self.storage.open(name=filepath, mode='rb')
