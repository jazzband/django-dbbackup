from dbbackup.storage.base import BaseStorage


class FakeStorage(BaseStorage):
    name = 'FakeStorage'
    list_files = ['foo', 'bar']
    deleted_files = []

    def delete_file(self, filepath):
        self.deleted_files.append(filepath)

    def list_directory(self, raw=False):
        return self.list_files

    def write_file(self, filehandle, filename):
        pass

    def read_file(self, filepath):
        pass
