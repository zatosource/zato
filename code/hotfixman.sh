#!/bin/bash

CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

FULL_VERSION=$($CURDIR/bin/zato --version 2>&1)
VERSION=$($CURDIR/bin/python -c "print('$FULL_VERSION'.split()[1])" 2>&1)

if [[ -z "$ZATO_HOTFIXES_SOURCE" ]]
then
    HOTFIXES_SOURCE=common
else
    HOTFIXES_SOURCE=$ZATO_HOTFIXES_SOURCE
fi

# Attempt to download hotfixes for the given version and confirm it's actually bzip2
# because a file will be created regardless of whether it is an actual set of hotfixes
# or an HTML 404 error page.
curl https://zato.io/hotfixes/$HOTFIXES_SOURCE/hotfixes-$VERSION.tar.bz2 -o $CURDIR/hotfixes/hotfixes-$VERSION.tar.bz2 > /dev/null 2>&1

IS_BZIP2=$(file $CURDIR/hotfixes/hotfixes-$VERSION.tar.bz2 | grep bzip2)
if [[ -z "$IS_BZIP2" ]]
then
    echo "No hotfixes for $FULL_VERSION ($HOTFIXES_SOURCE)"
    rm -f $CURDIR/hotfixes/hotfixes-$VERSION.tar.bz2
    exit 0
fi

mkdir -p $CURDIR/hotfixes/backups-$VERSION
rm -rf $CURDIR/hotfixes/hotfixes-$VERSION
tar xvfj $CURDIR/hotfixes/hotfixes-$VERSION.tar.bz2 -C $CURDIR/hotfixes
rsync -abvv --suffix=_`date +"%Y%m%d_%H_%M_%S"` --backup-dir $CURDIR/hotfixes/backups-$VERSION $CURDIR/hotfixes/hotfixes-$VERSION/ $CURDIR

echo "Installed hotfixes for $FULL_VERSION"
