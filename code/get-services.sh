#!/bin/bash

declare -a repos
declare -a workdirs

repos=(
appzipper
configmanager
credentialsmanager
dbconnector
dbmanager
descriptionxml
devicemanager
feedbackmanager
licensemanager
mailingservice
organizationmanager
servicemanager
sqlalchemymodels
)

workdirs=(
appcloud
extra-libs
services
)

echo "Creating directories to store Zato services and server objects..."
for dir in ${workdirs[@]}
do
    if [ ! -d $HOME/$dir ]
    then
        mkdir $HOME/$dir
        echo "Directory $dir created."
    fi
done
cd $HOME/appcloud

echo "Cloning repositories and copying services..."
for repo in ${repos[@]}
do
    if [ ! -d appcloud.$repo ]
    then
        git clone git@bitbucket.org:foxway/appcloud.$repo.git
        if [ $repo = "sqlalchemymodels" ]
        then
            cd appcloud.$repo/uploads
            cp ./*py $HOME/extra-libs
            cd ../..
        else
            cd appcloud.$repo
            cp ./*.py $HOME/services
            cd ..
        fi
    fi
done
