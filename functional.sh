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
    touch ${MEDIA_ROOT}foo
    mkdir -p ${MEDIA_ROOT}bar
    touch ${MEDIA_ROOT}bar/ham

    $PYTHON runtests.py mediabackup --no-compress

    rm -rf ${MEDIA_ROOT}*
    $PYTHON runtests.py mediarestore --noinput
}

test_media_results () {
    media_success=0
    [[ -f ${MEDIA_ROOT}foo ]] || media_success=1
    [[ -d ${MEDIA_ROOT}bar ]] || media_success=1
    [[ -f ${MEDIA_ROOT}bar/ham ]] || media_success=1
    [[ "$media_success" -eq 0 ]] && echo "Media test succeed!" || echo "Media test failed!"
}


main () {
    if [[ -z "$DATABASE_URL" ]]; then
        DATABASE_FILE="$(mktemp)"
        export DATABASE_URL="sqlite:///$DATABASE_FILE"
    fi
    export PYTHON=${PYTHON:-python}
    export STORAGE="dbbackup.storage.filesystem_storage"
    export STORAGE_LOCATION="/tmp/backups/"
    export STORAGE_OPTIONS="location=${STORAGE_LOCATION}"
    export MEDIA_ROOT="/tmp/media/"

    make_db_test 
    test_db_results

    mkdir -p $STORAGE_LOCATION
    mkdir -p $MEDIA_ROOT
    make_media_test 
    test_media_results

    [[ -n "$DATABASE_FILE" ]] && rm "$DATABASE_FILE"
    rm -rf "$MEDIA_ROOT"

    return $((db_success + media_success))
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main || exit 1
fi
