"""
Dropbox API Storage object.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import pickle
import os
import tempfile
import io
from django.conf import settings
from dropbox import session
from dropbox.client import DropboxClient
from dropbox.rest import ErrorResponse
from shutil import copyfileobj
from .base import BaseStorage, StorageError

DEFAULT_ACCESS_TYPE = 'app_folder'
MAX_SPOOLED_SIZE = 10 * 1024 * 1024
FILE_SIZE_LIMIT = 145 * 1024 * 1024


################################
#  Dropbox Storage Object
################################

class Storage(BaseStorage):
    """ Dropbox API Storage. """
    name = 'Dropbox'
    TOKENS_FILEPATH = getattr(settings, 'DBBACKUP_TOKENS_FILEPATH', None)
    DROPBOX_DIRECTORY = getattr(settings, 'DBBACKUP_DROPBOX_DIRECTORY', '').strip('/')
    DBBACKUP_DROPBOX_APP_KEY = getattr(settings, 'DBBACKUP_DROPBOX_APP_KEY', None)
    DBBACKUP_DROPBOX_APP_SECRET = getattr(settings, 'DBBACKUP_DROPBOX_APP_SECRET', None)
    DBBACKUP_DROPBOX_ACCESS_TYPE = getattr(settings, 'DBBACKUP_DROPBOX_ACCESS_TYPE', DEFAULT_ACCESS_TYPE)
    _request_token = None
    _access_token = None

    def __init__(self, server_name=None):
        self._check_settings()
        self.dropbox = self.get_dropbox_client()
        BaseStorage.__init__(self)

    def _check_settings(self):
        """ Check we have all the required settings defined. """
        if not self.TOKENS_FILEPATH:
            raise StorageError('Dropbox storage requires DBBACKUP_TOKENS_FILEPATH to be defined in settings.')
        if not self.DBBACKUP_DROPBOX_APP_KEY:
            raise StorageError('%s storage requires DBBACKUP_DROPBOX_APP_KEY to be defined in settings.' % self.name)
        if not self.DBBACKUP_DROPBOX_APP_SECRET:
            raise StorageError('%s storage requires DBBACKUP_DROPBOX_APP_SECRET to be specified.' % self.name)

    ###################################
    #  DBBackup Storage Methods
    ###################################

    def backup_dir(self):
        return self.DROPBOX_DIRECTORY

    def delete_file(self, filepath):
        """ Delete the specified filepath. """
        files = self.list_directory(raw=True)
        to_be_deleted = [x for x in files if os.path.splitext(x)[0] == filepath]
        for name in to_be_deleted:
            self.run_dropbox_action(self.dropbox.file_delete, name)

    def list_directory(self, raw=False):
        """ List all stored backups for the specified. """
        metadata = self.run_dropbox_action(self.dropbox.metadata, self.DROPBOX_DIRECTORY)
        filepaths = [x['path'] for x in metadata['contents'] if not x['is_dir']]
        if not raw:
            filepaths = [os.path.splitext(x)[0] for x in filepaths]
            filepaths = list(set(filepaths))
        return sorted(filepaths)

    def get_numbered_path(self, path, number):
        return "{0}.{1}".format(path, number)

    def write_file(self, filehandle, filename):
        """ Write the specified file. """
        filehandle.seek(0)
        total_files = 0
        path = os.path.join(self.DROPBOX_DIRECTORY, filename)
        for chunk in self.chunked_file(filehandle):
            self.run_dropbox_action(self.dropbox.put_file,
                self.get_numbered_path(path, total_files), chunk)
            total_files += 1

    def read_file(self, filepath):
        """ Read the specified file and return it's handle. """
        total_files = 0
        filehandle = tempfile.SpooledTemporaryFile(max_size=MAX_SPOOLED_SIZE)
        try:
            while True:
                response = self.run_dropbox_action(self.dropbox.get_file,
                    self.get_numbered_path(filepath, total_files),
                    ignore_404=(total_files > 0))
                if not response:
                    break
                copyfileobj(response, filehandle)
                total_files += 1
        except:
            filehandle.close()
            raise
        return filehandle

    def run_dropbox_action(self, method, *args, **kwargs):
        """ Check we have a valid 200 response from Dropbox. """
        ignore_404 = kwargs.pop("ignore_404", False)
        try:
            response = method(*args, **kwargs)
        except ErrorResponse as e:
            if ignore_404 and e.status == 404:
                return None
            errmsg = "ERROR %s" % (e,)
            raise StorageError(errmsg)
        return response

    ###################################
    #  Dropbox Client Methods
    ###################################

    def get_dropbox_client(self):
        """ Connect and return a Dropbox client object. """
        self.read_token_file()
        sess = session.DropboxSession(self.DBBACKUP_DROPBOX_APP_KEY,
            self.DBBACKUP_DROPBOX_APP_SECRET, self.DBBACKUP_DROPBOX_ACCESS_TYPE)
        # Get existing or new access token and use it for this session
        access_token = self.get_access_token(sess)
        sess.set_token(access_token.key, access_token.secret)
        dropbox = DropboxClient(sess)
        # Test the connection by making call to get account_info
        dropbox.account_info()
        return dropbox

    def get_request_token(self, sess):
        """ Return Request Token. If not available, a new one will be created, saved
            and a RequestUrl object will be returned.
        """
        if not self._request_token:
            return self.create_request_token(sess)
        return self._request_token

    def create_request_token(self, sess):
        """ Return Request Token. If not available, a new one will be created, saved
            and a RequestUrl object will be returned.
        """
        self._request_token = sess.obtain_request_token()
        self.save_token_file()
        return self._request_token

    def prompt_for_authorization(self, sess, request_token):
        """ Generate the authorization url, show it to the user and exit """
        message = "Dropbox not authorized, visit the following URL to authorize:\n"
        message += sess.build_authorize_url(request_token)
        raise StorageError(message)

    def get_access_token(self, sess):
        """ Return Access Token. If not available, a new one will be created and saved. """
        if not self._access_token:
            return self.create_access_token(sess)
        return self._access_token

    def create_access_token(self, sess):
        """ Create and save a new access token to self.TOKENFILEPATH. """
        request_token = self.get_request_token(sess)
        try:
            self._access_token = sess.obtain_access_token(request_token)
        except ErrorResponse:
            # If we get an error, it means the request token has expired or is not authorize, generate a new request
            # token and prompt the user to complete the authorization process
            request_token = self.create_request_token(sess)
            self.prompt_for_authorization(sess, request_token)
        # We've got a good access token, save it.
        self.save_token_file()
        return self._access_token

    def save_token_file(self):
        """ Save the request and access tokens to disk. """
        tokendata = dict(request_token=self._request_token, access_token=self._access_token)
        with open(self.TOKENS_FILEPATH, 'wb') as tokenhandle:
            pickle.dump(tokendata, tokenhandle, -1)

    def read_token_file(self):
        """ Reload the request and/or access tokens from disk. """
        if os.path.exists(self.TOKENS_FILEPATH):
            with open(self.TOKENS_FILEPATH, 'rb') as tokenhandle:
                tokendata = pickle.load(tokenhandle)
            self._request_token = tokendata.get('request_token')
            self._access_token = tokendata.get('access_token')

    @staticmethod
    def chunked_file(filehandle, chunk_size=FILE_SIZE_LIMIT):
        eof = False
        while not eof:
            tmpfile = io.BytesIO()
            chunk_space = chunk_size
            while chunk_space > 0:
                data = filehandle.read(min(16384, chunk_space))
                if not data:
                    eof = True
                    break
                chunk_space -= len(data)
                tmpfile.write(data)
            if tmpfile.tell() > 0:
                tmpfile.seek(0)
                yield tmpfile
            tmpfile.close()
