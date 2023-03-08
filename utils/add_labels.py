from utils import settings
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Generate new text files with all labels: old & new")
    parser.add_argument("object_labels_path", type=str, help=(
        "Full path to the directory containing existing labels (object)."
    ))
    parser.add_argument("no_object_labels_path", type=str, help=(
        "Full path to the directory containing new labels (no object)."
    ))
    parser.add_argument("target_labels_path", type=str, help=(
    "Full path to the directory for the resulting labels (object + no object)."
    ))
    args = parser.parse_args()
    return args

### ORIGINAL DATASET ###
source_path = settings.DATASET_PATH
labels_path = os.path.join(source_path, 'labels')

### SUBSET FOLDER ###
destination_path = settings.SUBSET_PATH
images_path = os.path.join(destination_path, 'images')
new_labels_path = os.path.join(destination_path, 'new_labels')
target_path = os.path.join(destination_path, 'labels')

def add_labels():
    subset = os.listdir(images_path)
    new_labels = os.listdir(new_labels_path)

    for image_name in subset:
        image_name = image_name.split('.')[0]
        old_bbs = os.path.join(labels_path, image_name+'.txt')
        new_bbs = os.path.join(new_labels_path, image_name+'.txt')

        if (image_name+'.txt') in new_labels:
            os.makedirs(target_path, exist_ok=True)
            with open(os.path.join(target_path, image_name+'.txt'), 'a+') as target:
                with open(old_bbs, 'r') as l1:
                    with open(new_bbs, 'r') as l2:
                        target.write(l1.read())
                        target.write(l2.read())
        else:
            os.link(old_bbs, os.path.join(target_path, image_name+'.txt'))

    print('Done')

if __name__ == '__main__':
    add_labels()   
