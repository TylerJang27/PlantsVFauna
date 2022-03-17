# PlantsVFauna
Upstream communication for the PestPro project.

https://mosquitto.org/download/

# Install Procedure
1. `./docker_install.sh`
2. Follow on-screen prompts
3. If mistakes occur, edit in `db.env`

# Simulate Procedure
1. `sudo docker-compose up --build database broker website`
2. `sudo docker-compose up --build mqtt` (another terminal)
3. `cd mqtt_device`
4. `python3 .`

# Run Procedure


