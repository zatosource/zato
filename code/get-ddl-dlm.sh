#!/bin/bash -eux

repo=databases.foxwayid
workdir=sql

echo "Creating a directory to store database objects..."
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

echo "Copying database objects to a separate directory..."
cp -r $HOME/$repo/*.sql $HOME/$workdir
if [ $? == 0 ]
then
    echo "Database objects copied."
else
    echo "ERROR - Database objects not copied."
fi
