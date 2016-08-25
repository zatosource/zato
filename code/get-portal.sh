#!/bin/bash

repo=foxway.foxwayops

if [ ! -d $HOME/$repo ]
then
    cd $HOME
    git clone git@bitbucket.org:foxway/$repo.git
else
    cd $HOME/$repo
    git pull
fi


echo "Install Portal's dependencies..."
$HOME/.local/bin/pip install -r $HOME/$repo/requirements.txt --user

# Ensure that there is the latest version of pyScss installed
$HOME/.local/bin/pip uninstall pyScss --yes
$HOME/.local/bin/pip install pyScss
