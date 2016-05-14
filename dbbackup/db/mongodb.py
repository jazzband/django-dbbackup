from .base import BaseCommandDBConnetor


class MongoDumpConnector(BaseCommandDBConnetor):
    """
    MongoDB connector, creates dump with ``mongodump`` and restore with
    ``mongorestore``.
    """
    dump_cmd = 'mongodump'
    restore_cmd = 'mongorestore'

    def create_dump(self, exclude=None):
        cmd = '%s --db %s' % (self.dump_cmd, self.settings['NAME'])
        cmd += ' --host %s:%s' % (self.settings['HOST'], self.settings['PORT'])
        cmd += ' --username %s' % self.settings['USER']
        cmd += ' --password %s' % self.settings['PASSWORD']
        for collection in exclude or []:
            cmd += ' --excludeCollection %s' % collection
        cmd += ' -'
        return self.run_command(cmd)

    def restore_dump(self, dump, object_check=True, drop=True):
        cmd = self.restore_cmd
        cmd += ' --host %s:%s' % (self.settings['HOST'], self.settings['PORT'])
        cmd += ' --username %s' % self.settings['USER']
        cmd += ' --password %s' % self.settings['PASSWORD']
        if object_check:
            cmd += ' --objcheck'
        if drop:
            cmd += ' --drop'
        return self.run_command(cmd, stdin=dump)
