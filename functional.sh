#!/bin/bash
export DATABASE_URL="sqlite:///test-sqlite"
export STORAGE="dbbackup.storage.filesystem_storage"
export STORAGE_OPTIONS="location=/tmp/"

python runtests.py migrate
python runtests.py dbbackup
python runtests.py dbrestore --noinput
