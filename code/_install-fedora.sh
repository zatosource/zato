#!/bin/bash

#
# Taken from https://gist.github.com/josephwecker/2884332
#
CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

function symlink_py {
    ln -s `python -c 'import '${1}', os.path, sys; sys.stdout.write(os.path.dirname('${1}'.__file__))'` $CURDIR/zato_extra_paths
}

bash $CURDIR/clean.sh

FOX_HOME=/home/foxway
MIRROR_OS=http://mirror.centos.org/centos/6/os/x86_64/Packages

mkdir $FOX_HOME/rpms
wget -P $FOX_HOME/rpms \
    $MIRROR_OS/bzip2-devel-1.0.5-7.el6_0.x86_64.rpm \
    $MIRROR_OS/bzr-2.1.1-2.el6.x86_64.rpm \
    $MIRROR_OS/gcc-c++-4.4.7-17.el6.x86_64.rpm \
    $MIRROR_OS/gcc-gfortran-4.4.7-17.el6.x86_64.rpm \
    $MIRROR_OS/git-1.7.1-4.el6_7.1.x86_64.rpm \
    $MIRROR_OS/haproxy-1.5.4-3.el6.x86_64.rpm \
    $MIRROR_OS/libevent-devel-1.4.13-4.el6.x86_64.rpm \
    $MIRROR_OS/libffi-devel-3.0.5-3.2.el6.x86_64.rpm \
    $MIRROR_OS/libxml2-devel-2.7.6-21.el6.x86_64.rpm \
    $MIRROR_OS/libxslt-devel-1.1.26-2.el6_3.1.x86_64.rpm \
    $MIRROR_OS/libyaml-devel-0.1.3-4.el6_6.x86_64.rpm \
    $MIRROR_OS/openssl-1.0.1e-48.el6.x86_64.rpm \
    $MIRROR_OS/openssl-devel-1.0.1e-48.el6.x86_64.rpm \
    $MIRROR_OS/python-devel-2.6.6-64.el6.x86_64.rpm \
    $MIRROR_OS/swig-1.3.40-6.el6.x86_64.rpm \
    $MIRROR_OS/uuid-1.6.1-10.el6.x86_64.rpm \
    $MIRROR_OS/uuid-devel-1.6.1-10.el6.x86_64.rpm \
    $MIRROR_OS/gcc-4.4.7-17.el6.x86_64.rpm \
    $MIRROR_OS/libevent-doc-1.4.13-4.el6.noarch.rpm \
    $MIRROR_OS/libevent-headers-1.4.13-4.el6.noarch.rpm \
    $MIRROR_OS/libgcrypt-devel-1.4.5-11.el6_4.x86_64.rpm \
    $MIRROR_OS/libgfortran-4.4.7-17.el6.x86_64.rpm \
    $MIRROR_OS/libstdc++-4.4.7-17.el6.x86_64.rpm \
    $MIRROR_OS/libstdc++-devel-4.4.7-17.el6.x86_64.rpm \
    $MIRROR_OS/libxml2-2.7.6-21.el6.x86_64.rpm \
    $MIRROR_OS/libxslt-1.1.26-2.el6_3.1.x86_64.rpm \
    $MIRROR_OS/libyaml-0.1.3-4.el6_6.x86_64.rpm \
    $MIRROR_OS/perl-Error-0.17015-4.el6.noarch.rpm \
    $MIRROR_OS/perl-Git-1.7.1-4.el6_7.1.noarch.rpm \
    $MIRROR_OS/python-2.6.6-64.el6.x86_64.rpm \
    $MIRROR_OS/python-libs-2.6.6-64.el6.x86_64.rpm \
    $MIRROR_OS/python-paramiko-1.7.5-2.1.el6.noarch.rpm \
    $MIRROR_OS/rsync-3.0.6-12.el6.x86_64.rpm \
    $MIRROR_OS/cpp-4.4.7-17.el6.x86_64.rpm \
    $MIRROR_OS/libgcc-4.4.7-17.el6.x86_64.rpm \
    $MIRROR_OS/libgomp-4.4.7-17.el6.x86_64.rpm \
    $MIRROR_OS/libgpg-error-devel-1.7-4.el6.x86_64.rpm \
    $MIRROR_OS/python-crypto-2.0.1-22.el6.x86_64.rpm

for file in $(ls $FOX_HOME/rpms/)
do
    rpm2cpio $FOX_HOME/rpms/$file > $FOX_HOME/rpms/$file.cpio
done

for cpio in $(ls $FOX_HOME/rpms/ | grep .cpio)
do
    cpio -idv < $FOX_HOME/rpms/$cpio
done

export PATH=$PATH:$FOX_HOME/usr/bin/

#mkdir $CURDIR/zato_extra_paths

#export CYTHON=$CURDIR/bin/cython

#sudo pip-python install --upgrade pip
#sudo pip-python install distribute==0.6.49
#sudo pip-python install virtualenv==1.9.1
#sudo pip-python install zato-apitest

#virtualenv .

#$CURDIR/bin/python bootstrap.py -v 1.7.0
#$CURDIR/bin/buildout

echo
echo OK
