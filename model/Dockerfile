# FROM python:3.8.13 as base

# ADD requirements.txt .
# # RUN apt update; apt install -y libgl1
# RUN apt-get update && apt-get install -y python3-opencv
# RUN pip3 install -r requirements.txt
# RUN pip install -r https://raw.githubusercontent.com/ultralytics/yolov5/master/requirements.txt

# ENV PYTHONPATH=$PYTHONPATH:/src/

# ADD ./ /src/

# WORKDIR /src

# FROM base as test
# RUN ["pytest", "-v", "/src/tests"]

# FROM base as build
# ENTRYPOINT ["python3", "/src/ml_service.py"]

#######################################################

# Yolov5 DockerFile for cpu modified
# YOLOv5 🚀 by Ultralytics, GPL-3.0 license
# Builds ultralytics/yolov5:latest-cpu image on DockerHub https://hub.docker.com/r/ultralytics/yolov5
# Image is CPU-optimized for ONNX, OpenVINO and PyTorch YOLOv5 deployments

# Start FROM Ubuntu image https://hub.docker.com/_/ubuntu
FROM ubuntu:20.04 as base

# Downloads to user config dir
ADD https://ultralytics.com/assets/Arial.ttf https://ultralytics.com/assets/Arial.Unicode.ttf /root/.config/Ultralytics/

# Install linux packages
RUN apt update
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt install -y tzdata
RUN apt install --no-install-recommends -y python3-pip git zip curl htop libgl1-mesa-glx libglib2.0-0 libpython3.8-dev

# Install pip packages
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip
RUN pip install --no-cache -r requirements.txt albumentations gsutil notebook \
    coremltools onnx onnx-simplifier onnxruntime openvino-dev tensorflow-cpu tensorflowjs \
    --extra-index-url https://download.pytorch.org/whl/cpu

ENV PYTHONPATH=$PYTHONPATH:/src/

ADD ./ /src/

WORKDIR /src

FROM base as test
RUN ["pytest", "-v", "/src/tests"]

FROM base as build
ENTRYPOINT ["python3", "/src/ml_service.py"]