#!/bin/bash

# Copyright (C) 2022, Zato Source s.r.o. https://zato.io

git log -n 1 --pretty=format:"%H" > `pwd`/code/release-info/revision.txt
