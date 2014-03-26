#!/bin/bash

CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

function symlink_py {
    ln -s `python -c 'import '${1}', os.path, sys; sys.stdout.write(os.path.dirname('${1}'.__file__))'` $CURDIR/zato_extra_paths
}

rm -rf $CURDIR/bin
rm -rf $CURDIR/develop-eggs
rm -rf $CURDIR/downloads
rm -rf $CURDIR/eggs
rm -rf $CURDIR/include
rm -rf $CURDIR/.installed.cfg
rm -rf $CURDIR/.coverage
rm -rf $CURDIR/lib
rm -rf $CURDIR/local
rm -rf $CURDIR/parts
rm -rf $CURDIR/zato_extra_paths

find $CURDIR -name \*.pyc -delete 
