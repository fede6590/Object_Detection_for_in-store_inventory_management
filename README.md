# Object detection for in-store inventory management

The main objective of this project is to build a solution to detect objects in shelves for in-store inventory management. The dataset contains densely packed objects taken from multiple angles, lighting conditions, and situations.

References:
* Precise Detection in Densely Packed Scenes (paper): https://arxiv.org/abs/1904.00853
* YOLO v5 code implementation: https://github.com/ultralytics/yolov5
* How to train YOLO v5 with custom data: https://github.com/ultralytics/yolov5/wiki/Train-Custom-Data (or this tutorial: https://blog.paperspace.com/train-yolov5-custom-data/)

## TRAIN

YOLO: https://github.com/ultralytics/yolov5/wiki

PAPER: https://paperswithcode.com/sota/dense-object-detection-on-sku-110k

To build Docker image for yolov5 (in model/yolov5 folder):
```
docker build -t yolo_v5_image -f utils/docker/Dockerfile .
```

To run Docker from the server in the project folder using yolo_v5_image:
```
docker run --rm --net host -it --gpus all -v $(pwd):/home/app/src --workdir /home/app/src yolo_v5_image bash
```
(also see https://github.com/ultralytics/yolov5/wiki/Docker-Quickstart)

To run the trainning inside Docker, go to model/yolov5 and run:
```
python train.py --img 640 --batch 16 --epochs 30 --data SKU-110K-subset.yaml --weights ../import/best_stripped.pt
```

Or stay in the project folder and run:
```
python model/yolov5/train.py --img 640 --batch 16 --epochs 30 --data SKU-110K-subset.yaml --weights model/import/best_stripped.pt
```

Once the training started (tmux recommended), run tensorboard:
```
tensorboard --logdir model/yolov5/runs/train
```

## DETECT

To run the microservices, run:
```
docker compose up --build -d
```

Then, open the browser and access: localhost:5005
