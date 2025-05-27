sudo apt-get update
sudo apt-get install -y git
curl -sSL https://get.docker.com | sh
sudo apt-get install -y uidmap
dockerd-rootless-setuptool.sh install
systemctl --user (start|stop|restart) docker.service
echo "export PATH=/usr/bin:$PATH" >> ~/bash.rc
echo "export DOCKER_HOST=unix:///run/user/1000/docker.sock"
sudo systemctl enable docker
sudo loginctl enable-linger blower
sudo apt install python3 python3-pip python3-dev python3-venv build-essential
