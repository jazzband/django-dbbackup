FAQ
===

**ERROR [403] The provided token does not allow this operation**

   Creating an app in Dropbox defaults access to "app_folder" as opposed
   to whole folder. Try changing the setting DBBACKUP_DROPBOX_ACCESS_TYPE
   to 'app_folder'. (Ref: issue #9)
