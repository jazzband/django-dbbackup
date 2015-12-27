#!/bin/bash
export DATABASE_URL="sqlite:///test-sqlite"
export STORAGE="dbbackup.storage.filesystem_storage"
export STORAGE_OPTIONS="location=/tmp/"
python tests/runtests.py migrate
python tests/runtests.py dbbackup
python tests/runtests.py dbrestore --noinput
