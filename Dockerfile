FROM balenalib/n510-tx2-python

RUN apt-get update &&\
    apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install opencv-python flask
