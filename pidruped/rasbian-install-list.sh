### Set up wifi
sudo vim /etc/wpa_supplicant/wpa_supplicant.conf
# add wifi settings per network:
network={
    ssid="HOME NETWORK NAME"
    psk="HOME PASSWORD"
    id_str="home"
}

### Packages
sudo apt-get install vim tmux
sudo apt-get install git
sudo apt-get install python-pip python-dev
sudo apt-get install libblas-dev liblapack-dev libatlas-base-dev gfortran

### Install python libraries for Adafruit Servo/PWM Pi Hat && turn on I2C kernel module
# https://learn.adafruit.com/adafruit-16-channel-pwm-servo-hat-for-raspberry-pi/overview
# https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c
sudo apt-get install python-smbus
sudo apt-get install i2c-tools
sudo raspi-config #turn on I2C kernel module in Advanced Options
# reboot
# check for I2C connected devices
sudo i2cdetect -y 1

### Adafruit code for the Servo Hat 
git clone -b legacy https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code.git
# cd Adafruit-Raspberry-Pi-Python-Code/Adafruit_PWM_Servo_Driver

### Accelerometer lib
git clone https://github.com/pimoroni/adxl345-python

### Python packages
sudo pip install numpy
sudo pip install scipy
sudo pip install sklearn
sudo apt-get install libhdf5-dev
sudo pip install h5py
sudo pip install gym

### TensorFlow, https://github.com/samjabrahams/tensorflow-on-raspberry-pi
wget https://github.com/samjabrahams/tensorflow-on-raspberry-pi/raw/master/bin/tensorflow-0.9.0-cp27-none-linux_armv7l.whl
sudo pip install tensorflow-0.9.0-cp27-none-linux_armv7l.whl
