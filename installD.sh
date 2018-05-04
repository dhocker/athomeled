#!/bin/bash

### Install athomeledD.sh as a daemon

# Installation steps
sudo cp athomeledD.sh /etc/init.d/athomeledD.sh
sudo chmod +x /etc/init.d/athomeledD.sh
sudo update-rc.d athomeledD.sh defaults

# Start the daemon: 
sudo service athomeledD.sh start

exit 0

