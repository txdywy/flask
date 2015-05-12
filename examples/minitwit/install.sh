#!/bin/bash
if [ -f /usr/local/bin/pip ] || [ -f /usr/bin/pip ];
then
    echo "pip exists"
else
    echo "Installing pip"
    wget https://bootstrap.pypa.io/get-pip.py
    python get-pip.py
fi
sudo apt-get install gcc g++ python-dev postfix mysql-python sqlite
sudo pip install fabric
python deploy.py
