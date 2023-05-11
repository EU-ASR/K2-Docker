# Sherpa Docker info 

For Jupyter:
* Needs `bash` kernel not Python
* To allow scrollable output for Jupyter outputs 
* Interactive (waiting for user input) shell commands does not work in notebook because they block and wait for the user input...


```bash
# Convert this notebook to markdown format file sherpa.md
jupyter nbconvert --to markdown sherpa.ipynb
```


## Install Docker

To install docker engine you can follow the original guide for your os
[Install Docker Engine](https://docs.docker.com/engine/install/)

or use the following version for ubuntu

### Install

Official Guide: [Install on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

If on Ubuntu then you can install Docker with



```bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```


And test if it's installed



```bash
sudo docker run hello-world
```

### Linux post-install

Note that the command after install was run with sudo, to manage docker as non-root user complete 
[linux post-install](https://docs.docker.com/engine/install/linux-postinstall/)



```bash
sudo groupadd docker
sudo usermod -aG docker $USER
```


than logout and login to activate changes to groups and run



```bash
newgrp docker
docker run hello-world
```


To configure Docker to start on boot with systemd you need to run




```bash
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
```

## Building image

The images are built in CI/CD pipelines, however we can build them locally.

Building image with specified Dockerfile `linux-64-cpu-python.Dockerfile` from root project directory:



```bash
docker build -f linux-64-cpu-python.Dockerfile --tag sherpa-python:linux-64-cpu .
```


you can view the image with 




```bash
docker image ls
```


or remove it with



```bash
docker image rm $IMAGE_ID
```

where `IMAGE_ID` is short unique image hash such as `b273004037cc`. There is also command `docker prune` or `docker image prune` which can be quite usefull for clean-up

## Pulling image

To pull already build image from remote Docker container registry https://github.com/Andyy42/sherpa/pkgs/container/sherpa (this one is GitHub Container Registry - **ghcr**).  you can run




```bash
docker pull ghcr.io/andyy42/sherpa:dockerfile-linux-64-cpu
```

## Docker lifecycle

Simplified version of Docker lifecycle

![Docker lifecycle](https://k21academy.com/wp-content/uploads/2020/10/Capture-5.png)


## Running containers 

Image which is currently used is called conatiner. To run container interactively do


```bash
docker run --rm -ti ghcr.io/andyy42/sherpa:dockerfile-linux-64-cpu
```


```bash
docker run --rm -ti --entrypoint bash ghcr.io/andyy42/sherpa:dockerfile-linux-64-cpu
```



where `--rm` automatically removes container when in exists, `-t` allocates pseudo-TTY and `-i` will
enter interactive mode (keep STDIN open even if not attached).

The running Docker container will start `bash` shell from which you can use it.
Note that containers have usually specified `ENTRYPOINT`
which can be a start-up script for webserver or any other script. To override it
we run `--entrypoint bash`. 




Now we are in `bash`, try to play with it. To detach from such container we can do `CTRL+P`, `CTRL+Q`
but the container is till running in the background and we can return to it but first we need the container id!
To list **running** only containers do: 


```bash
docker ps
```

We can either use `CONTAINER_ID` or `NAME`, we'll go with `CONTAINER_ID` for now and attach to the container:


```bash
CONTAINER_ID=PUT_ID_HERE
docker attach $CONTAINER_ID
```

We can also execute something inside the Docker container (this will run separately from currently running process inside the container)


```bash
docker exec -ti $CONTAINER_ID bash
```

To get image ID use `docker container ls` to list running containers. To remove this container
we can either use 


```bash
docker container stop $CONTAINER_ID 
docker container rm $CONTAINER_ID 
```


or simply exit from the atteched container (becuase we used the `--rm` flag)

We can also use this command:


```bash
docker run --rm -ti ghcr.io/andyy42/sherpa:dockerfile-linux-64-cpu sherpa-version
```



where the entrypoint is used the defualt (bash in this case) and runs commands passed to it
which are after image tag `ghcr.io/andyy42/sherpa:dockerfile-linux-64-cpu`, which is `sherpa-version`
in this case.



## Docker and volumes 

* Volumes https://docs.docker.com/storageo/volumes/
* Bind mounts https://docs.docker.com/storage/bind-mounts/
* `tmpfs` mounts (not important for us and not used very often)

![Volumes with docker](https://docs.docker.com/storage/images/types-of-mounts-volume.png)

**NOTE:** Both volumes and bind mounts are created with `-v`, `--volume` or `--mount` (mount is more verbose).

### Note about users, groups and file permissions

* To simplify, Docker can be viewed as a combination of `cgroups` and `namespaces`.
* `namespaces` are used to isoloate **host user:group** space from the container's **user:group space**.

If running docker root-less you do it by defining mapping for the user which currently runs the docker. Container's UID and GID starts from that number. The mapping is specified in:
```bash
/etc/subuid # For UID
/etc/subgid # For GID
```
So user with UID 0 is mapped to a starting number (100000 for example) in `\etc\subuid`. This might cause issues with permissions!

Easy workaround is to set correct permissions for the folder we want to use as a volume. Or if we do not care about permissions in our current sitation just use:


```bash
sudo chmod -R 0777 <path_to_dir> 
```

*NOTE: chmod 0777 is workaround, there is better option to manage permissions!*

Or you can create some technical user like `docker-root` which maps to `root` user in running container (they have same ID in host OS)

## Pre-trained models demo

To try pretrained models you can use **sherpa** documentation: [Pre-trained models for C++ users](https://k2-fsa.github.io/sherpa/cpp/pretrained_models/offline_ctc/icefall.html)


### [Offline transducer models](https://k2-fsa.github.io/sherpa/cpp/pretrained_models/offline_transducer.html)
#### icefall-asr-gigaspeech-conformer-ctc (English)

This section is copied from the documentation. Firstly download the model with `git lfs pull`: 


```bash
# This model is trained using GigaSpeech + LibriSpeech with zipformer
#
# See https://github.com/k2-fsa/icefall/pull/728
#
GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/WeijiZhuang/icefall-asr-librispeech-pruned-transducer-stateless8-2022-12-02
cd icefall-asr-librispeech-pruned-transducer-stateless8-2022-12-02
git lfs pull --include "exp/cpu_jit-torch-1.10.pt"
git lfs pull --include "data/lang_bpe_500/LG.pt"

cd exp
rm cpu_jit.pt
ln -sv cpu_jit-torch-1.10.pt cpu_jit.pt
cd ..
```

Now run the container with:


```bash
docker run --rm -ti -v $(pwd)/icefall-asr-librispeech-pruned-transducer-stateless8-2022-12-02/:/opt/models/icefall-asr-librispeech-pruned-transducer-stateless8-2022-12-02 \
  -p 6006:6006--entrypoint bash --name sherpa ghcr.io/andyy42/sherpa:dockerfile-linux-64-cpu \
```


```bash
MODEL=/opt/models/icefall-asr-librispeech-pruned-transducer-stateless8-2022-12-02
# Decode with H
sherpa-offline \
  --nn-model=$MODEL/exp/cpu_jit.pt \
  --hlg=$MODEL/data/lang_bpe_500/HLG.pt \
  --tokens=$MODEL/data/lang_bpe_500/tokens.txt \
  $MODEL/test_wavs/1089-134686-0001.wav \
  $MODEL/test_wavs/1221-135766-0001.wav \
  $MODEL/test_wavs/1221-135766-0002.wav

# Decode with HLG
sherpa-offline \
  --nn-model=$MODEL/exp/cpu_jit.pt \
  --hlg=$MODEL/data/lang_bpe_500/HLG.pt \
  --tokens=$MODEL/data/lang_bpe_500/tokens.txt \
  $MODEL/test_wavs/1089-134686-0001.wav \
  $MODEL/test_wavs/1221-135766-0001.wav \
  $MODEL/test_wavs/1221-135766-0002.wav
```

Or we can mount `models/` dir from our local filesystem to `/opt/models` in docker container filesystem with `-v /path/to/models:/opt/models`

### [Online transducer models](https://k2-fsa.github.io/sherpa/cpp/pretrained_models/online_transducer.html)
(did not work: `icefall-asr-librispeech-pruned-transducer-stateless7-streaming-2022-12-29`)

#### icefall-asr-librispeech-conv-emformer-transducer-stateless2-2022-07-05



```bash
# This model is trained using LibriSpeech with ConvEmformer transducer
#
# See https://github.com/k2-fsa/icefall/pull/440
#
GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/Zengwei/icefall-asr-librispeech-conv-emformer-transducer-stateless2-2022-07-05
cd icefall-asr-librispeech-conv-emformer-transducer-stateless2-2022-07-05

git lfs pull --include "exp/cpu-jit-epoch-30-avg-10-torch-1.10.0.pt"
git lfs pull --include "data/lang_bpe_500/LG.pt"
cd exp
ln -sv cpu-jit-epoch-30-avg-10-torch-1.10.0.pt cpu_jit.pt
cd ..
```


```bash
docker run --rm -ti -v $(pwd)/icefall-asr-librispeech-conv-emformer-transducer-stateless2-2022-07-05/:/opt/models/icefall-asr-librispeech-pruned-transducer-stateless8-2022-12-02 \
  -p 6006:6006--entrypoint bash --name sherpa ghcr.io/andyy42/sherpa:dockerfile-linux-64-cpu \
```


```bash
MODEL=/opt/models/icefall-asr-librispeech-conv-emformer-transducer-stateless2-2022-07-05
for m in greedy_search modified_beam_search fast_beam_search; do
  sherpa-online \
    --decoding-method=$m \
    --nn-model=$MODEL/exp/cpu_jit.pt \
    --tokens=$MODEL/data/lang_bpe_500/tokens.txt \
    $MODEL/test_wavs/1089-134686-0001.wav \
    $MODEL/test_wavs/1221-135766-0001.wav \
    $MODEL/test_wavs/1221-135766-0002.wav
done

# For fast_beam_search with LG
sherpa-online \
  --decoding-method=fast_beam_search \
  --nn-model=$MODEL/exp/cpu_jit.pt \
  --lg=./data/lang_bpe_500/LG.pt \
  --tokens=$MODEL/data/lang_bpe_500/tokens.txt \
  $MODEL/test_wavs/1089-134686-0001.wav \
  $MODEL/test_wavs/1221-135766-0001.wav \
  $MODEL/test_wavs/1221-135766-0002.wav
```

Or we can mount `models/` dir from our local filesystem to `/opt/models` in docker container filesystem with `-v /path/to/models:/opt/models`

### Docker-compose


Running containers with `docker run` is nice but imagine you have to spin up three containers, create networking for them, add volumes etc...

Fortunately, `docker-compose` comes to rescue and we can define how will the docker containers run with code.

The shell command: 
```bash
docker run --rm -ti -v /path/to/models/:/opt/models/ \
  -p 6006:6006--entrypoint bash --name sherpa ghcr.io/andyy42/sherpa:dockerfile-linux-64-cpu \
```

Can be roughly re-written to `docker-compose.yml`:
```yaml
services:
    sherpa:
        image: ghcr.io/andyy42/sherpa:dockerfile-linux-64-cpu
        ports: 6006:6006
        volumes:
            -  /path/to/models/:/opt/models/
        entrypoint:
            - bash
```

It introduces new commands:


```bash
docker-compose up           # Starts all services (containers)
docker-compose down         # Stops and remove containers, networks, ...
docker-compose run $SERVICE # Runs one-off command on a service (can also start single service such as `sherpa`)
docker-compose stop         # Stops running containers
docker-compose start        # Start stopped containers
docker-compose build        # Build/rebuild services if `build` defined
...
```

### IIS proj example

This is just and *illustrative example* how to use `docker-compose` in context of web app to show it's potential.

Web app with:
* Django (Python) **backend** - `backend` service
* React (JS) **frontend** - static frontend served by `nginx` service
* Postgres **database** - `db` service
* nginx **reverse proxy** which also serves static frontend - `nginx` service

```yaml
---
version: '3'

services:
    db:
        env_file:
            - .env.local
        image: postgres:14-alpine
        volumes:
            - ./data/db:/var/lib/postgresql/data
    backend:
        build:
            context: .
            dockerfile: ./docker/backend/Dockerfile
        entrypoint: /app/docker/backend/wsgi-entrypoint.sh
        expose:
            - 8000
        environment:
            - DOCKER_COMPOSE=1
        restart: unless-stopped
        volumes:
            - static_volume:/app/backend/django_static
        depends_on:
            - db
    nginx:
        build:
            context: .
            dockerfile: ./docker/nginx/Dockerfile
        depends_on:
            - backend
        ports:
            - '80:80'
        restart: unless-stopped
        volumes:
            - static_volume:/app/backend/django_static
            - ./docker/nginx/development:/etc/nginx/conf.d

volumes:
    static_volume: {}
```

### Docker-compose in sherpa

More complex example how to use `docker-compose` with sherpa to automate `docker` commands

`.env` file with pre-populated variables:
```bash
SHERPA_TAG=dockerfile-linux-64-cpu
SHERPA_COMMAND=sherpa-offline-websocket-server
SHERPA_COMMAND_EXTRA_ARGS="--max-utterance-length=300"
SHERPA_TOKENS_PATH=data/lang_bpe_500/tokens.txt
SHERPA_NN_MODEL_PATH=exp/cpu_jit.pt
SHERPA_PORT=6006
SHERPA_MODEL_NAME=icefall-asr-librispeech-pruned-transducer-stateless8-2022-12-02
SHERPA_MODEL_PATH="../../models"
```



`docker-compose.yml` with definitions how to compose docker:
```yaml
version: "3.8"
services:
  sherpa:
    image: "ghcr.io/andyy42/sherpa:${SHERPA_TAG}"
    entrypoint:
      - ${SHERPA_COMMAND}
      - --port=6006
      - --use-gpu=false
      - --num-io-threads=3
      - --num-work-threads=5
      - --max-batch-size=5
      - --nn-model=/opt/models/${SHERPA_MODEL_NAME}/${SHERPA_NN_MODEL_PATH}
      - --tokens=/opt/models/${SHERPA_MODEL_NAME}/${SHERPA_TOKENS_PATH}
      - --decoding-method=greedy_search
      - --log-file=/var/log/sherpa.log
      - --doc-root=/app/sherpa/web/
      - ${SHERPA_COMMAND_EXTRA_ARGS:---}}
    working_dir: /app/sherpa
    ports:
      - ${SHERPA_PORT}:6006
    volumes:
      - ${SHERPA_MODEL_PATH}:/opt/models/
```

With `docker-compose` you can specify different `.env` files with `--env-file`
or `docker-compose.yml` with `--file`


```bash
docker-compose --file docker-compose.yml --env-file online.env up
```


```bash
docker-compose --file docker-compose.yml --env-file offline.env up
```

### Demo with [Ngrok](https://ngrok.com/docs/)

`ngrok` is the fastest way to host and secure your applications and services on the internet.
It is good for quick testing. Creates tunnel with specified port and opens it to the internet.


```bash
ngrok http 6006 --region eu
```

`Websocket` endpoints work through ngrok's `http` tunnels without any changes. Or you can open `tcp` port directly as


```bash
ngrok tcp 6006 --region eu
```

**NOTE:** ngrok defualt region is not `eu` (Frankfurt) but `usa`

---

NOTE: I found it quite usefull to use ChatGPT4 for Docker commands or even better
with [shell GPT](https://github.com/TheR1D/shell_gpt) command `sgpt`.

TODO: Networking between several docker containers was not fully covered

TODO: Docker volumes for models (there are more options..)
