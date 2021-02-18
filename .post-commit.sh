#!/bin/bash

git log -n 1 --pretty=format:"%H" > `pwd`/code/release-info/revision.txt

# Please ignore this comment
