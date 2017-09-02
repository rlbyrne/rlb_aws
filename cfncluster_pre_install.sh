#!/bin/bash

#basic installations and updates:
sudo apt-get -y update
sudo apt-get -y install awscli
aws configure <<< $'AKIAIBZCNKF2RGOPI4GA\n3mu+g/1ubVsBDuikYzEUbcLkxQTpGtMC2fzTt7eg\nus-east-1\n\n' #inputs AWS Access Key, AWS Secret Access Key, Default region name, and Default ouput format
sudo apt-get -y install python-pip python-dev build-essential
sudo pip install --upgrade pip
sudo pip install --upgrade virtualenv
sudo pip install --upgrade cfncluster


#download the following from S3:
#Miniconda2-latest-Linux-x86_64.sh
#IDL_8.2.iso
#license.dat (IDL license)
#astron.zip (IDL astronomy library)
#coyoteprograms.zip (IDL coyotegraphics library)
#MWA_Tools
#FHD
#rlb_aws
aws s3 cp s3://mwatest/FHD_install.tar ~
tar -xvf FHD_install.tar


#install Miniconda
sudo bash ~/Miniconda2-latest-Linux-x86_64.sh -b #-b runs in batch mode (no user input required)
echo 'export PATH="/home/ubuntu/miniconda2/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc


#install IDL
sudo apt-get -y install xorg openbox
#sudo apt-get -y install libXp6 #for Ubuntu 14
sudo chmod a+w /etc/apt/sources.list
echo "deb http://security.ubuntu.com/ubuntu precise-security main" >> /etc/apt/sources.list
sudo apt update
sudo apt install libxp6

sudo mkdir ~/IDL_iso
sudo mount -o loop -n ~/IDL_8.2.iso ~/IDL_iso
sudo mkdir /usr/local/exelis
sudo bash ~/IDL_iso/install_unix.sh #requires user input
sudo mv ~/license.dat /usr/local/exelis/license/license.dat
sudo bash /usr/local/exelis/idl82/bin/lmgrd -c /usr/local/exelis/license/license.dat #hangs at the end, requires user input

sudo mkdir ~/MWA
sudo unzip ~/astron.zip -d ~/MWA/astron
sudo unzip ~/coyoteprograms.zip -d ~/MWA/coyote
sudo mv ~/MWA_Tools ~/MWA/MWA_Tools
sudo mv ~/FHD ~/MWA/FHD
sudo mv ~/rlb_aws ~/MWA/rlb_aws

# 8/30 RERUN THESE!!!:
echo 'export PATH="/home/ubuntu/MWA/rlb_aws:$PATH"' >> ~/.bashrc
echo 'export PATH="/home/ubuntu/MWA/FHD:$PATH"' >> ~/.bashrc
echo 'export IDL_PATH=$IDL_PATH:+"~/MWA/astron"' >> ~/.bashrc
echo 'export IDL_PATH=$IDL_PATH:+"~/MWA/coyote"' >> ~/.bashrc
echo 'export IDL_PATH=$IDL_PATH:+"~/MWA/FHD"' >> ~/.bashrc
echo 'export IDL_PATH=$IDL_PATH:+"~/MWA/MWA_Tools"' >> ~/.bashrc
echo 'export IDL_PATH=$IDL_PATH:+"/usr/local/exelis/idl82/lib"' >> ~/.bashrc


#cleanup
sudo bash /usr/local/sbin/ami_cleanup.sh
