FROM python:3.8.13 as base

ADD requirements.txt .
RUN pip3 install -r requirements.txt

ENV PYTHONPATH=$PYTHONPATH:/src/

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

ADD ./ /src/

WORKDIR /src

# FROM base as test
# RUN ["pytest", "-v", "/src/tests"]

FROM base as build
ENTRYPOINT ["gunicorn", "--workers=8", "--bind", "0.0.0.0:5000", "app:app", "--timeout", "180"]
