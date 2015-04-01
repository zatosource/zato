#!/bin/bash

#
# I'm just waiting for someone to tell me they use apt-get on RHEL
# or yum on Ubuntu. But I'm really not going to chase and compare all the options
# and environment variables various shells and distros use. (dsuch 1 VI 2013)
#
# Please help out with it by advocating among your distribution's developers
# that Zato be included in your system as a package out of the box instead. Many thanks!
#

CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

git log -n 1 --pretty=format:"%H" > $CURDIR/release-info/revision.txt

IS_DEB=0
IS_RHEL=0

RUN=0

#
# What OS are we on
#

apt-get > /dev/null 2>&1
if (($? == 0)) ; then IS_DEB=1 ; fi

yum --help > /dev/null 2>&1
if (($? == 0)) ; then IS_RHEL=1 ; fi

#
# Run an OS-specific installer
#

if [ $IS_DEB -eq 1 ]
then
  bash $CURDIR/_install-deb.sh
  RUN=1
fi

if [ $IS_RHEL -eq 1 ]
then
  bash $CURDIR/_install-rhel.sh
  RUN=1
fi

#
# Unknown system
#

if [ $RUN -ne 1 ]
then
   echo "Could not find apt-get nor yum. OS could not be determined, installer cannot run."
   exit 1
fi
