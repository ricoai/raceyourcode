sudo apt-get update
#sudo apt-get install libblas-dev -y       ## 1-2 minutes
#sudo apt-get install liblapack-dev -y     ## 1-2 minutes
#sudo apt-get install python-dev -y        ## Optional]
#sudo apt-get install libatlas-base-dev -y ## Optional speed up execution]
#sudo apt-get install python3-h5py -y
#sudo apt-get install libhdf5-10 -y
#sudo apt-get install libhdf5-serial-dev -y
#sudo apt-get install libhdf5-dev -y
#sudo apt-get install libhdf5-cpp-11 -y

#source ricar_ryc/env/bin/activate
#pip install -r ricar_ryc/requirements_rpi.txt

mkdir ~/thunderborg
cd ~/thunderborg
wget https://www.piborg.org/downloads/thunderborg/examples.zip
unzip example.zip
chmod +x install.sh
./install.sh
sudo apt-get -y install python-picamera
sudo apt-get -y install libcv-dev libopencv-dev python-opencv

