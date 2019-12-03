### W251 Final Project

#### BEFORE DOING ANYTHING, CHANGE LINE 90 OF `./dockerfile_tx2_forwarder/scripts/tx2_forwarder_09_comments.py` TO YOUR VSI'S IP ADDRESS


## Create bridge networks on the TX2 and on the virtual server instance (VSI)
#### Create bridge network on TX2
```
docker network create --driver bridge final
```

#### Create bridge network on VSI
```
docker network create --driver bridge final
```


## Build docker containers 
#### Build `face_detector_fp` docker container while within `./dockerfile_face_detector` on the TX2
```
docker build -t face_detector_fp .
```

#### Build `tx2_forwarder_fp` docker container while within `./dockerfile_tx2_forwarder` on the TX2
```
docker build -t tx2_forwarder_fp .
```

#### Build `responder_fp` docker container while within `./dockerfile_responder` on the TX2
```
docker build -t responder_fp .
```

#### Build `adjudicator_fp` docker container while within `./dockerfile_adjudicator` on the VSI
```
docker build -t adjudicator_fp .
```


## Start docker containers and run scripts
#### Start mosquitto broker on TX2, opening port 1883. (The indented '#' denotes commands I ran from within the container.)
```
docker run --name mosquitto --network final -p 1883:1883 -ti alpine sh
   # apk update && apk add mosquitto && /usr/sbin/mosquitto
```

#### Log in to VSI and start mosquitto broker, opening port 1883. (The indented '#' denotes commands I ran from within the container.)
```
docker run --name mosquitto --network final -p 1883:1883 -ti alpine sh
   # apk update && apk add mosquitto && /usr/sbin/mosquitto
```

#### (OPTIONAL) Start an MQTT client to monitor incoming `adjudicator/#` messages on the TX2. (The indented '#' denotes commands I ran from within the container.)
```
docker run --name forwarder --network final -ti alpine sh
   # apk update && apk add mosquitto-clients
   # mosquitto_sub -h mosquitto -t adjudicator/#
```

#### (OPTIONAL) Start an MQTT client to monitor incoming `local/#` messages on the VSI. (The indented '#' denotes commands I ran from within the container.)
```
docker run --name forwarder --network final -ti alpine sh
   # apk update && apk add mosquitto-clients
   # mosquitto_sub -h mosquitto -t local/#
```

#### Start `adjudicator_fp` docker container on VSI 
```
docker run -it --network final --name adjudicator_fp adjudicator_fp

```

#### Start `tx2_forwarder_fp` docker container on TX2 and run `tx2_forwarder.py`. (The indented '#' denotes commands I ran from within the container.)
```
docker run -it --network final --name tx2_forwarder_fp tx2_forwarder_fp
   # python tx2_forwarder_09_comments.py
```

#### Start `face_detector_fp` docker container on TX2 and run `face_detector.py` script that takes images, identifies faces, and publishes the faces as messages to the "faces" topic on the TX2's mosquitto broker. (The indented '#' denotes commands I ran from within the container.)
```
docker run -it --device=/dev/video1:/dev/video1 --network final --name face_detector_fp face_detector_fp
   # python face_detector_06_comments.py
```

#### Start `responder_fp` docker container on TX2 and run `responder_07_comments.py`. (The indented '#' denotes commands I ran from within the container.) This should open a window that prompts you for an account number; you can enter anything here.
```
docker run -it --network final --name responder_fp responder_fp
   # python responder_07_comments.py
```

#### Once you enter an account number, `responder_fp` will send a message to `adjudicator_fp`, which will send a message that starts the camera on `face_detector_fp`. `face_detector_fp` will publish a set number of pictures, stop, and send a message that tells `adjudciator_fp` it's done. `adjudicator_fp` sends another message telling `face_detector_fp` to stop. 

#### `adjudicator_fp` is a dummy container that mimics the outputs from Vivek's face discriminator. Right now, it's set to tell you that the face recognition failed. You'll see a prompt appear in `responder_fp` that asks for a password. If you enter 'money', then you'll get a response that indicates you've passed. If you enter anything else, then you'll get a response that says you entered the wrong password. 
