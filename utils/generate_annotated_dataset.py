import cv2
import os
from tqdm import tqdm

from settings import DATASET_PATH

DIV_FACTOR = 333.33
SRC_DATASET_PATH = os.path.join(DATASET_PATH, 'images')
DST_DATASET_PATH = os.path.join(DATASET_PATH, 'annotated_images')
os.makedirs(DST_DATASET_PATH, exist_ok=True)
LABELS_PATH = os.path.join(DATASET_PATH, 'annotations')


def draw_bboxes(labels, img_name):
    """
    Draw bboxes and save the image.
    """

    # Load image
    img = cv2.imread(os.path.join(SRC_DATASET_PATH, img_name))

    # Get bounding boxes
    gt_bb = labels.loc[labels['image_name'] == img_name]

    # Bounding boxes color
    color = (0, 255, 0)
    
    # Calculate thickness
    dim_factor = (img.shape[0] + img.shape[1]) / 2
    thickness = int(dim_factor / DIV_FACTOR)

    for _, bb in gt_bb.iterrows():

        x1 = bb['x1']
        y1 = bb['y1']
        x2 = bb['x2']
        y2 = bb['y2']

        # Start coordinate, here (100, 50)
        # represents the top left corner of rectangle
        start_point = (x1, y1)
    
        # Ending coordinate, here (125, 80)
        # represents the bottom right corner of rectangle
        end_point = (x2, y2)
    
        # Using cv2.rectangle() method
        # Draw a rectangle of black color of thickness -1 px
        img = cv2.rectangle(img, start_point, end_point, color, thickness)

    # Save img
    cv2.imwrite(os.path.join(DST_DATASET_PATH, img_name), img)


def generate_dataset():
    col_names = ["image_name", "x1", "y1", "x2", "y2", "class", "image_width", "image_height"]

    labels_train = pd.read_csv(os.path.join(LABELS_PATH, "annotations_train.csv"), names=col_names)
    labels_val = pd.read_csv(os.path.join(LABELS_PATH, "annotations_val.csv"), names=col_names)
    labels_test = pd.read_csv(os.path.join(LABELS_PATH, "annotations_test.csv"), names=col_names)

    frames = [labels_train, labels_val, labels_test]

    labels = pd.concat(frames)

    images = os.listdir(SRC_DATASET_PATH)

    for img in tqdm(images):
        draw_bboxes(labels, img)


if __name__ == "__main__":
    generate_dataset()