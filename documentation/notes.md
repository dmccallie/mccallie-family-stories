## Quick notes to myself

### installing on a new windows WSL
```
    update wsl using:
    update ubuntu using:
    sudo apt update && apt install
```
#### install a general python 3.10 using:
```
    sudo apt update
    sudo apt install software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt install python3.10
    sudo apt intall python3.10-venv
    [remember to use "python3.10" when creating venv]
```

#### make sure pip is up to date and pointing to your 3.10 python!
```
    (see copilot help)
```

#### install local version of tailwindcss using:
NO, should not need to install this - done by pytailwindcss pip script
```
        curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
        chmod +x tailwindcss-linux-x64
        mv tailwindcss-linux-x64 tailwindcss [installs into home directory]
```

#### copy over .env and db.sqlite3 files from master source (not in github)
    
Remember to run tailwinds in separate process (during debug):

```
        (pytailwindcss should have installed this)
        tailwindcss -i static/src/input.css -o static/src/output.css --watch
```

### running the app locally:
```
    DEBUG=True python manage.py runserver 0.0.0.0:8000
    on windows had to run from 127.0.0.1:8000 ????
```

### initialize testing data
```
stuff goes here

```

### adding a new app, needs updates all over:
```
1. settings.py - add to INSTALLED_APPS = []
1. 
```

### deploy to vps
#### login to vps
```
ssh xxxxxx@yyyyyyy
```

#### copy stuff up
```
rsync -av --exclude-from='/home/david/python_projects/mccallie-family-stories/.rsync_exclude.txt' /home/david/python_projects/mccallie-family-stories/ xxxx@nn.nn.nn.nn:/home/david/python_projects/mccallie-family-stories
```

#### stop existing run
```
cd python_projects/mccallie-family-stories/
docker-compose down
docker-ps
docker stop xxxxxxxxx
```

#### build and deploy new version (can take a few mins)
```
docker-compose -f docker-compose-caddy.yml up --build -d
```
#### monitor logs
```
cd logs/caddy
sudo goaccess access.log --log-format=CADDY
```

