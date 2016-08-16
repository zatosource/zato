#!/bin/bash

repo=foxway.foxwayops

if [ ! -d $HOME/$repo ]
then
    cd $HOME
    git clone git@bitbucket.org:foxway/$repo.git
fi

echo "Install Portal's dependencies..."
$HOME/.local/bin/pip install -r $HOME/$repo/requirements.txt --user
