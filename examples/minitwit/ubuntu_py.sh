sudo apt update -y
sudo apt upgrade -y
sudo apt install htop git httping vnstat -y
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev -y
wget https://www.python.org/ftp/python/2.7.13/Python-2.7.13.tgz
gunzip Python-2.7.13.tgz
tar -xvf Python-2.7.13.tar
cd Python-2.7.13
./configure
make
sudo make install
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py 
sudo pip install uwsgi supervisor flask sqlalchemy
