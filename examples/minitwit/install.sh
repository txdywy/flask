#!/bin/bash
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
sudo apt-get install gcc g++ python-dev postfix
sudo pip install fabric
python deploy.py
