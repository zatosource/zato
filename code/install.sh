#!/bin/bash

#
# I'm just waiting for someone to tell me they use apt-get on SLES
# or yum on Ubuntu. But I'm really not going to chase and compare all the options
# and environment variables various shells and distros use. (dsuch 1 VI 2013)
#
# Please help out with it by advocating among your distribution's developers
# that Zato is included in your system as a package out of the box instead. Many thanks!
#

IS_DEB=0
IS_RHEL=0
IS_SLES=0
IS_DARWIN=0

RUN=0

apt-get > /dev/null 2>&1
if (($? == 0)) ; then IS_DEB=1 ; fi

yum > /dev/null 2>&1
if (($? == 0)) ; then IS_RHEL=1 ; fi

zypper > /dev/null 2>&1
if (($? == 0)) ; then IS_SLES=1 ; fi

brew > /dev/null 2>&1
if (($? == 0)) ; then IS_DARWIN=1 ; fi

if [ $IS_DEB -eq 1 ]
then
  bash ./_install-deb.sh
  RUN=1
fi

#
# IS_SLES must be checked before IS_RHEL
#

if [ $IS_SLES -eq 1 ]
then
  bash ./_install-sles.sh
  RUN=1
fi

if [ $IS_RHEL -eq 1 ]
then
  bash ./_install-rhel.sh
  RUN=1
fi

if [ $IS_SLES -eq 1 ]
then
  bash ./_install-rhel.sh
  RUN=1
fi

if [ $IS_DARWIN -eq 1 ]
then

  cp buildout.cfg buildout.cfg.bak
  cp versions.cfg versions.cfg.bak
  
  sed '/    console_scripts/d' ./buildout.cfg
  sed '/inotifyx/d' ./buildout.cfg
  
  sed '/inotifyx/d' ./version.cfg

  bash ./_install-darwin.sh
  RUN=1
fi

if [ $RUN -ne 1 ]
then
   echo "Could not find apt-get, yum, zypper nor brew. OS could not be determined, installer cannot run."
   exit 1
fi