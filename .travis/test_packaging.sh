#!/bin/bash

#
# Try running ./install.sh in the configured environment.
#

set -ex
source $TRAVIS_BUILD_DIR/.travis/setup.sh
run bash -ec "cd /tmp/zato/code && bash -ex ./install.sh -p ${PY_VERSION:-python}"


#
# Compare the result of 'pip freeze' with requirements.txt, fail the job if
# they materially differ.
#

SYS_PLATFORM=$(uname | tr '[A-Z]' '[a-z]')

normalize() {
    sort -f |\
    tr '[A-Z]' '[a-z'] |\
    grep -vE '^-e ' |\
    grep -vE 'suds-ovnicraft' |\
    grep -vE 'dpath' |\
    grep -vE 'globre' |\
    grep -vE 'inotifyx' |\
    cut -d';' -f1
}

# cat code/requirements.txt | normalize > /tmp/declared.txt
# run bash -c "source /tmp/zato/code/bin/activate > /dev/null ;/tmp/zato/code/bin/pip freeze" | normalize > /tmp/installed.txt
#
# echo
# echo
# echo '-- Comparing requirements.txt (declared) vs. "pip freeze" (installed) --'
# echo
# diff /tmp/declared.txt /tmp/installed.txt

#
# Job will fail when diff exit status != 0.
#
