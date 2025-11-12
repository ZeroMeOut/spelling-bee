
# Spelling Bee

Just a simple spelling bee game :) Here I would talk about how to run in your local machine and for deployment. All the coding was done on Linux (Fedora btw) so it might be different for other OS/distributions.







## Running Locally
Start off by installing redis
``` zsh
sudo dnf install redis    
sudo systemctl start redis
sudo systemctl enable redis
redis-cli ping
```
Create a venv with python 3.11 , I am using  `uv` here. Then install the dependencies
```python
uv venv name-of-venv --python 3.11
uv pip install -r requirements.txt
```
Git clone
```git
git clone https://github.com/ZeroMeOut/spelling-bee
cd spelling-bee
```
Run app
```bash
uvicorn app:app
```
## Deployment
For deployment I am using an EC2 instance be cause I don't want to set ElasticCache (I think that's the one) for Redis. I also just wanted to learn EC2 in general. Firstly you set up an EC2 instance. You can use [this](https://www.geeksforgeeks.org/devops/amazon-ec2-creating-an-elastic-cloud-compute-instance/) tutorial, just be sure to use Ubuntu instead of AWS linux (I find the former more convenient).
Then you ssh into it, create a `setup.sh` file with `vim setup.sh` and then paste the following
```bash
echo "Starting setup"

sudo apt update -y  && sudo apt upgrade -y
sudo apt install docker.io docker-compose git nginx -y

echo "Docker stuff"
sudo systemctl enable --now  docker
sudo groupadd docker
sudo usermod -aG docker $USER

echo "Git Stuff"
git clone https://github.com/ZeroMeOut/spelling-bee
cd spelling-bee

docker-compose up --build -d --remove-orphans

echo "Nginx stuff"
sudo tee /etc/nginx/sites-available/spelling-bee > /dev/null <<'EOF'
server {
        listen 80;
        server_name _;
        
        location / {
                 proxy_pass http://127.0.0.1:8000;
                 proxy_set_header Host $host;
                 proxy_set_header X-Real-IP $remote_addr;
                 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                 proxy_set_header X-Forwarded-Proto $scheme;
        }
}

EOF

sudo ln -s /etc/nginx/sites-available/spelling-bee /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

echo "Done"
```

Then just save it by pressing Esc to :wq and run by `bash setup.sh`.
I noticed that when the `docker-compose up --build -d --remove-orphans` runs the setup fails, but just just exit the instance and ssh into again, then run the shell file again. Idk why exactly it works but it does. [Here](https://stackoverflow.com/questions/64662372/docker-compose-up-error-while-fetching-server-api-version-connection-aborte) is where I found the solution :)
## Random Rambling
This project took me like a week to finish, could be less if I remove the days I was procrastinating lmao. At first I was using apis for the definitions and words but I then thought "Hmm I think I could make it all local", so I did with nltk's wordnet and brown. The set is umm alright and it did introduce me to LRU (Least-Recently-Used) cache which I didn't know existed. I should really read on that, I should read on a lot of things.

For the TTS model it's alright as well for a very light weight model. Honestly I just browsed through [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/) and picked the one that gave me less fraustation to setup. My friends are annoyed with it tho XD, so I am planning to using a more powerful TTS model and just store the audios in an S3 bucket or something.

Honestly learned a lot doing this, it was fun. I would make improvements here and there before moving to another project, and the site would keep running until it cooks my budget. Until the next :)
## Acknowledgements

 - [This wonderful channel](https://www.youtube.com/@pixegami)
 - [Another wonderful channel](https://www.youtube.com/@8nehe)
 - [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/)

