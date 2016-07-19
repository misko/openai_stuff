### Set up wifi
sudo vim /etc/network/interfaces

### Packages
sudo apt-get install vim
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
pip install scipy
pip install sklearn
pip install gym
pip install tensorflow
