#!/bin/bash

repo=foxway.ops.odb_config
workdir=server-objects

echo "Creating a directory to store server objects..."
if [ ! -d $HOME/$workdir ]
then
    mkdir $HOME/$workdir
    echo "Done."
fi

if [ ! -d $HOME/$repo ]
then
    cd $HOME
    git clone git@bitbucket.org:foxway/$repo.git
fi

echo "Copying server objects to a separate directory..."
cp -r $HOME/$repo/*.json $HOME/$workdir
if [ $? == 0 ]
then
    echo "Server objects copied."
else
    echo "ERROR - Server objects not copied."
fi
