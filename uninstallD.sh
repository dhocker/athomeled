#!/bin/bash

### Uninstall (remove) athomeledD.sh as a daemon

# Uninstall steps
sudo service athomeledD.sh stop
sudo rm /etc/init.d/athomeledD.sh
sudo update-rc.d -f athomeledD.sh remove 

exit 0

