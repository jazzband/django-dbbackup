#!/bin/bash

. functional.sh


backup () {
    $PYTHON runtests.py migrate --noinput || exit 1
    $PYTHON runtests.py feed
    $PYTHON runtests.py dbbackup
    count1=$($PYTHON runtests.py count)
}

restore () {
    $PYTHON runtests.py flush --noinput
    $PYTHON runtests.py dbrestore --noinput
    count2=$($PYTHON runtests.py count)
}

main () {
    if [[ -z "$DATABASE_URL" ]]; then
        DATABASE_FILE="$(mktemp)"
        export DATABASE_URL="sqlite:///$DATABASE_FILE"
    fi
    export PYTHON=${PYTHON:-python}
    export STORAGE="${STORAGE:-django.core.files.storage.FileSystemStorage}"
    export STORAGE_LOCATION="/tmp/backups/"
    export STORAGE_OPTIONS="${STORAGE_OPTIONS:-location=$STORAGE_LOCATION}"

    pip install 'django-dbbackup<3' -U
    backup

    pip install . -U
    restore

    test_db_results

    [[ -n "$DATABASE_FILE" ]] && rm "$DATABASE_FILE"

    return $((db_success))
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main || exit 1
fi
