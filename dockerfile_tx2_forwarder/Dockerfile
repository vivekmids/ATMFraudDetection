# Builds from an alpine OS with Python 2 installed. Adds paho-mqtt client

FROM seblucas/alpine-python2

# Install paho-mqtt
RUN pip install paho-mqtt

# Add `tx2_forwarder.py` script to local `scripts` directory
COPY scripts /
