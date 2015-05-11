#!/bin/bash
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
sudo apt-get install gcc g++ python-dev postfix mysql-python sqlite
sudo pip install fabric
python deploy.py
