#!/bin/bash
if [ -f /usr/local/bin/pip ] || [ -f /usr/bin/pip ];
then
    echo "pip exists"
else
    echo "Installing pip"
    wget https://bootstrap.pypa.io/get-pip.py
    sudo python get-pip.py
fi
sudo apt-get install gcc g++ python-dev postfix sqlite mysql-client libjpeg-dev libmysqlclient-dev
sudo pip install fabric
python deploy.py

if [ -f ./alancer.db ]
then
    echo "alancer.db exists"
else
    openssl enc -des -d -a -in alancer_db_enc -out alancer.db
fi

if [ -d ./logs ]
then
    echo "logs exists"
else
    mkdir logs
    touch logs/uwsgi.log logs/error.log logs/serori.log
fi

