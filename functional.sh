#!/bin/bash

make_db_test () {
    $PYTHON runtests.py migrate --noinput || exit 1

    $PYTHON runtests.py feed
    $PYTHON runtests.py dbbackup
    count1=$($PYTHON runtests.py count)

    $PYTHON runtests.py flush --noinput

    $PYTHON runtests.py dbrestore --noinput
    count2=$($PYTHON runtests.py count)
}

test_db_results () {
    if [[ "$count1" -eq "$count2" ]] ; then
        echo 'DB test succeed!'
        db_success=0
    else
        echo 'DB test Failed!'
        db_success=1
    fi
}

make_media_test () {
    echo foo > ${MEDIA_ROOT}foo
    mkdir -p ${MEDIA_ROOT}bar
    echo ham > ${MEDIA_ROOT}bar/ham

    $PYTHON runtests.py mediabackup

    rm -rf ${MEDIA_ROOT}*
    $PYTHON runtests.py mediarestore --noinput
}

test_media_results () {
    media_success=0
    [[ -f ${MEDIA_ROOT}foo ]] || media_success=1
    [[ $(cat ${MEDIA_ROOT}foo) -eq foo ]] || media_success=1
    [[ -d ${MEDIA_ROOT}bar ]] || media_success=1
    [[ $(cat ${MEDIA_ROOT}bar/ham) -eq ham ]] || media_success=1
    [[ -f ${MEDIA_ROOT}bar/ham ]] || media_success=1
    [[ "$media_success" -eq 0 ]] && echo "Media test succeed!" || echo "Media test failed!"
}


main () {
    if [[ -z "$DB_ENGINE" ]] || [[ "$DB_ENGINE" = "django.db.backends.sqlite3" ]]; then
        if [[ -z "$DB_NAME" ]]; then
            export DB_NAME="$(mktemp)"
        fi
    fi
    export PYTHON=${PYTHON:-python}
    export STORAGE="${STORAGE:-django.core.files.storage.FileSystemStorage}"
    export STORAGE_LOCATION="/tmp/backups/"
    export STORAGE_OPTIONS="${STORAGE_OPTIONS:-location=$STORAGE_LOCATION}"
    export MEDIA_ROOT="/tmp/media/"

    make_db_test
    test_db_results

    mkdir -p $STORAGE_LOCATION
    mkdir -p $MEDIA_ROOT
    make_media_test
    test_media_results

    if [[ -z "$DB_ENGINE" ]] || [[ "$DB_ENGINE" = "django.db.backends.sqlite3" ]]; then
        rm "$DB_NAME"
    fi
    rm -rf "$MEDIA_ROOT"

    return $((db_success + media_success))
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main || exit 1
fi
