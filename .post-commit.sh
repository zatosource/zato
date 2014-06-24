#!/bin/bash

git log -n 1 --pretty=format:"%H" > `pwd`/code/zato-common/src/zato/common/revision.zato
