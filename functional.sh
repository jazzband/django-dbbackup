#!/bin/bash

make_test () {
    $PYTHON runtests.py migrate --noinput || exit 1

    $PYTHON runtests.py feed
    $PYTHON runtests.py dbbackup
    count1=$($PYTHON runtests.py count)

    $PYTHON runtests.py flush --noinput

    $PYTHON runtests.py dbrestore --noinput
    count2=$($PYTHON runtests.py count)
}

test_results () {
    if [[ "$count1" -eq "$count2" ]] ; then
        echo 'Success!'
        success=0
    else
        echo 'Failed!'
        success=1
    fi
}

main () {
    if [[ -z "$DATABASE_URL" ]]; then
        DATABASE_FILE="$(mktemp)"
        export DATABASE_URL="sqlite:///$DATABASE_FILE"
    fi
    export STORAGE="dbbackup.storage.filesystem_storage"
    export STORAGE_OPTIONS="location=/tmp/"
    export PYTHON=${PYTHON:-python}

    make_test 
    test_results

    [[ -n "$DATABASE_FILE" ]] && rm "$DATABASE_FILE"
    return $success
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main || exit 1
fi
