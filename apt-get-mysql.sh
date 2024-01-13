#!/bin/bash

# Update the package index
sudo apt-get update

# Install MySQL server and client
sudo apt-get install mysql-server mysql-client

# Start MySQL service
sudo service mysql start

# Display MySQL version
mysql --version