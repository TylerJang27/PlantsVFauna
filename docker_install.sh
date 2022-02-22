#!/bin/bash

sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --batch --yes --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io -y
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Set up development tools
sudo apt install python3-pip postgresql-client -y

# Set up environment files
DBENV=db.env
if [[ -f "$DBENV" ]]; then
    echo "DB environment file already exists"
else
    while read -s -p "Enter database password (cannot include characters: '/:@') and press [ENTER]: " dbpasswd; do
        if [ -z "$dbpasswd" ]; then
            echo ""
            continue
        fi
        break
    done
    user=`whoami`
    echo -e "\nAssuming your database user name is: $user"

    cp db-template.env db.env
    sed -i "s/db_user/$user/g" db.env
    sed -i "s/db_passwd/$dbpasswd/g" db.env

    secret=`tr -dc 'a-z0-9-_' < /dev/urandom | head -c50`
    sed -i "s/default_secret/'$secret'/g" db.env

    while read -s -p "Enter a password for admin@example.com and press [ENTER]: " adminpasswd; do
        if [ -z "$adminpasswd" ]; then
            echo ""
            continue
        fi
        break
    done
    sed -i "s/admin_password/$adminpasswd/g" db.env

    echo "Written DB environment file"
fi
