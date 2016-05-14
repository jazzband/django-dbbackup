from .base import BaseCommandDBConnetor


class MongoDumpConnetor(BaseCommandDBConnetor):
    """
    MongoDB connector, creates dump with ``mongodump`` and restore with
    ``mongorestore``.
    """
    def create_dump(self):
        cmd = 'mongodump'
        cmd += ' --host %s:%i' % (self.settings['HOST'], self.settings['PORT'])
        cmd += ' --username %s' % self.settings['USER']
        cmd += ' --password %s' % self.settings['PASSWORD']
        return self.run_command(cmd)

    def restore_dump(self, dump):
        cmd = 'mongorestore'
        cmd += ' --host %s:%i' % (self.settings['HOST'], self.settings['PORT'])
        cmd += ' --username %s' % self.settings['USER']
        cmd += ' --password %s' % self.settings['PASSWORD']
        return self.run_command(cmd, stdin=dump)
