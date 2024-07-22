
# AI-Chess Backend

Backend Deployment for My Reinforcement Learning Based Chess-AI model

## Technology Used - Flask, AWS EC2
## Run Locally

Clone the project

```bash
  git clone https://github.com/singhvaibhav924/Chess-AI-Backend.git
```

Go to the project directory

```bash
  cd my-project
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  python ./app.py
```

Note - Make sure to use virtualenv before installing the above packages to separate the installations from your system's other installations

## Deploy on AWS EC2

Create an EC2 Instance and add the below bash script in the User-Data field present in the advanced settings.
```bash
#!/bin/bash

sudo apt update && sudo apt upgrade -y
sudo apt install -y software-properties-common wget
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.9 python3.9-distutils python3.9-venv nginx git

wget https://bootstrap.pypa.io/get-pip.py
sudo python3.9 get-pip.py
rm get-pip.py

git clone https://github.com/singhvaibhav924/Chess-AI-Backend.git /home/ubuntu/Chess-AI-Backend
cd /home/ubuntu/Chess-AI-Backend

python3.9 -m venv venv
source venv/bin/activate && pip install -r requirements.txt && pip install gunicorn

cat << EOF | sudo tee /etc/systemd/system/Chess-AI-Backend.service
[Unit]
Description=Gunicorn instance for Chess AI Backend
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/Chess-AI-Backend
ExecStart=/home/ubuntu/Chess-AI-Backend/venv/bin/gunicorn -b localhost:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start Chess-AI-Backend
sudo systemctl enable Chess-AI-Backend

sudo systemctl start nginx
sudo systemctl enable nginx

# Configure Nginx
cat << EOF | sudo tee /etc/nginx/sites-available/Chess-AI-Backend
upstream chessai {
server 127.0.0.1:8000;
}

server {
listen 80;
server_name _;

location / {
proxy_pass http://chessai;
proxy_set_header Host \$host;
proxy_set_header X-Real-IP \$remote_addr;
proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto \$scheme;
}
}
EOF

sudo ln -s /etc/nginx/sites-available/Chess-AI-Backend /etc/nginx/sites-enabled

sudo rm /etc/nginx/sites-enabled/default

sudo nginx -t

sudo systemctl restart nginx

sudo ufw allow 'Nginx Full'
```
And Done!!!


![Static Badge](https://img.shields.io/badge/AI-For_Life-blue)
