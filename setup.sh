#!/bin/bash

BREW_CMD=$(which brew)
APT_CMD=$(which apt-get)

if [[ ! -z $BREW_CMD ]]; then
    echo "Installing python3...";
    brew install python3

elif [[ ! -z $APT_CMD ]]; then
    echo "Installing python3...";
    sudo apt-get install -y python3 python3-pip
else
    echo "Neither brew nor apt-get are installed.  Exiting..."
    exit 1;
fi

echo "Installing virtualenv and autoenv...";
pip3 install virtualenv autoenv

if ! grep -q "activate.sh" ~/.bashrc ; then
    read -r -p "Do you want to add autoenv to your ~/.bashrc (recommended)? [y/N] " response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]
    then
        echo "Adding autoenv to ~/.bashrc...";
        echo "# Activate autoenv" >> ~/.bashrc
        echo "source `which activate.sh`" >> ~/.bashrc
        echo "cd ." >> ~/.bashrc
    fi    
fi

if [ ! -d "env" ]; then
    echo "Creating virtual env..."
    virtualenv -p python3 env
fi