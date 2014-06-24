#!/bin/bash

git log -n 1 --pretty=format:"%H" > `pwd`/release-info/revision.txt
