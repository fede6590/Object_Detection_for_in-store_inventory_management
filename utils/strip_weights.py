from model.yolov5.utils.general import strip_optimizer
from utils.settings import WEIGHTS_PATH
import os

filename = input("Enter weights filename (without .pt extention):")
weight2strip = os.path.join(WEIGHTS_PATH, f'{filename}.pt')

strip_optimizer(weight2strip, os.path.join(WEIGHTS_PATH, f"{filename}_stripped.pt"))