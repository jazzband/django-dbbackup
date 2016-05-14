from .base import BaseCommandDBConnetor


class MysqlDumpConnetor(BaseCommandDBConnetor):
    def create_dump(self):
        host = self.connection.settings_dict.get('HOST', 'localhost')
        port = self.connection.settings_dict.get('PORT', 3306)
        user = self.connection.settings_dict['USER']
        password = self.connection.settings_dict.get('PASSWORD')
        database = self.connection.settings_dict['NAME']
        cmd = 'mysqldump %s' % database
        cmd += ' --host=%s' % host
        cmd += ' --port=%i' % port
        cmd += ' --user=%s' % user
        cmd += ' --password=%s' % password
        return self.run_command(cmd)

    def restore_dump(self, dump):
        conn_params = self.connection.settings_dict
        cmd = 'mysql %s' % conn_params['NAME']
        cmd += ' --host=%s' % conn_params.get('HOST', 'localhost')
        cmd += ' --port=%i' % conn_params.get('PORT', 3306)
        cmd += ' --user=%s' % conn_params['USER']
        cmd += ' --password=%s' % conn_params.get('PASSWORD')
        return self.run_command(cmd, stdin=dump)
