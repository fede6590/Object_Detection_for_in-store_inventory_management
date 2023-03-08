import argparse
import os
from PIL import Image
from utils import walkdir
import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser(description="Remove corrupted images.")
    parser.add_argument("images_folder", type=str, help=(
        "Full path to the directory having all the dataset images. E.g. "
        "`/home/app/src/data/images/`."
        ),
        )
    parser.add_argument(
        "annotations_folder",
        type=str,
        help=(
            "Full path to the CSV file with data labels. E.g. "
            "`/home/app/src/data/annotations`."
        ),
    )
    args = parser.parse_args()
    return args

def main(images_folder, annotations_folder):
    count = 0
    for path, filename in walkdir(images_folder):
        try:
            img = Image.open(os.path.join(path, filename))
            img.verify()
        except(IOError,SyntaxError):
            os.remove(os.path.join(path, filename))
            #remove from annotation
            dataset = 'annotations_' + filename.split('_')[0] + '.csv'
            ds_path = os.path.join(annotations_folder, dataset)
            col_names = ["image_name", "x1", "y1", "x2", "y2", "class", "image_width", "image_height"]
            temp_df = pd.read_csv(ds_path, names = col_names, index_col = 0)
            temp_df = temp_df.drop(filename,axis="index")
            temp_df.to_csv(ds_path)
            count = count + 1
    print("Corrupted images removed")
    print(f"{count} images removed")

if __name__ == "__main__":
    args = parse_args()
    main(args.images_folder, args.annotations_folder)