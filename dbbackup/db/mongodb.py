from .base import BaseCommandDBConnector


class MongoDumpConnector(BaseCommandDBConnector):
    """
    MongoDB connector, creates dump with ``mongodump`` and restore with
    ``mongorestore``.
    """
    dump_cmd = 'mongodump'
    restore_cmd = 'mongorestore'
    object_check = True
    drop = True

    def _create_dump(self):
        cmd = '{} --db {}'.format(self.dump_cmd, self.settings['NAME'])
        cmd += ' --host {}:{}'.format(self.settings['HOST'], self.settings['PORT'])
        if self.settings.get('USER'):
            cmd += ' --username {}'.format(self.settings['USER'])
        if self.settings.get('PASSWORD'):
            cmd += ' --password {}'.format(self.settings['PASSWORD'])
        for collection in self.exclude:
            cmd += ' --excludeCollection {}'.format(collection)
        cmd += ' --archive'
        cmd = '{} {} {}'.format(self.dump_prefix, cmd, self.dump_suffix)
        stdout, stderr = self.run_command(cmd, env=self.dump_env)
        return stdout

    def _restore_dump(self, dump):
        cmd = self.restore_cmd
        cmd += ' --host {}:{}'.format(self.settings['HOST'], self.settings['PORT'])
        if self.settings.get('USER'):
            cmd += ' --username {}'.format(self.settings['USER'])
        if self.settings.get('PASSWORD'):
            cmd += ' --password {}'.format(self.settings['PASSWORD'])
        if self.object_check:
            cmd += ' --objcheck'
        if self.drop:
            cmd += ' --drop'
        cmd += ' --archive'
        cmd = '{} {} {}'.format(self.restore_prefix, cmd, self.restore_suffix)
        return self.run_command(cmd, stdin=dump, env=self.restore_env)
