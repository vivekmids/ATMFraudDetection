# This Docker container has everything needed to run the USB camera, capture
# images, recoginze faces, and publish to a mosquitto broker

FROM cudabase:dev

# Make non-interactive to skip over installation prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install OpenCV, pip, and the paho-mqtt module
RUN apt update && apt install -y libopencv-dev python-opencv python-pip vim-tiny && pip install paho-mqtt 

# Be sure to add `haarcascade_frontalface_default.txt` and Python script to the 
# local `scripts` directory
COPY scripts /
