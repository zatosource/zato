#!/bin/bash

#
# I'm just waiting for someone to tell me they use apt-get on Fedora
# or yum on Ubuntu. But I'm really not going to chase and compare all the options
# and environment variables various shells and distros use. (dsuch 1 VI 2013)
#
# Please help out with it by advocating among your distribution's developers
# that Zato be included in your system as a package out of the box instead. Many thanks!
#

CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

cd /home/foxway/opt/zato/2.0.7/code/
git log -n 1 --pretty=format:"%H" > ./release-info/revision.txt

IS_DEB=0
IS_RHEL=0
IS_DARWIN=0

RUN=0

#
# What OS are we on
#

apt-get -v > /dev/null 2>&1
if (($? == 0)) ; then IS_DEB=1 ; fi

yum --help > /dev/null 2>&1
if (($? == 0)) ; then IS_RHEL=1 ; fi

brew --help > /dev/null 2>&1
if (($? == 0)) ; then IS_DARWIN=1 ; fi

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
  echo "Adding identity to the authentication client..."
  eval `ssh-agent -s`
  ssh-add $HOME/.ssh/zato_deploy
  bash $CURDIR/install-python2.7.sh
  bash $CURDIR/install-redis.sh
  bash $CURDIR/install-bzr.sh
  bash $CURDIR/install-haproxy.sh
  bash $CURDIR/_install-rhel.sh
  bash $CURDIR/get-services.sh
  bash $CURDIR/get-server-objects.sh
  bash $CURDIR/get-ddl-dlm.sh
  bash $CURDIR/create-package.sh
  RUN=1
fi

if [ $IS_DARWIN -eq 1 ]
then
  bash $CURDIR/_install-darwin.sh
  RUN=1
fi

#
# Unknown system
#

if [ $RUN -ne 1 ]
then
   echo "Could not find apt-get, yum nor brew. OS could not be determined, installer cannot run."
   exit 1
fi
