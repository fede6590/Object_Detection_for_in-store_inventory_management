from hashlib import md5
from os.path import splitext, join
from PIL import Image
import numpy as np
import cv2
import settings

ALLOWED_IMG_EXT = {".png", ".jpg", ".jpeg", ".gif"}
DIV_FACTOR = 333.33

def allowed_file(filename):
    """
    Checks if the format for the file received is acceptable. For this
    particular case, we must accept only image files.

    Parameters
    ----------
    filename : str
        Filename from werkzeug.datastructures.FileStorage file.

    Returns
    -------
    bool
        True if the file is an image, False otherwise.
    """

    _, ext = splitext(filename)
    ext = ext.lower()

    valid_file = ext in ALLOWED_IMG_EXT

    return valid_file


def get_file_hash(file):
    """
    Returns a new filename based on the file content using MD5 hashing.
    It uses hashlib.md5() function from Python standard library to get
    the hash.

    Parameters
    ----------
    file : werkzeug.datastructures.FileStorage
        File sent by user.

    Returns
    -------
    str
        New filename based in md5 file hash.
    """

    _, ext = splitext(file.filename)
    readable_hash = md5(file.read()).hexdigest()
    hash_filename = f"{readable_hash}{ext}"
    file.stream.seek(0)

    return hash_filename


def draw_bboxes(pred_data, img_name):
    """
    Draw bboxes and save the image.
    """

    # Load image
    img = cv2.imread(join(settings.UPLOAD_FOLDER, img_name))

    # Get bounding boxes
    bboxes = pred_data['bboxes']

    # Bounding boxes color
    color = (0, 255, 0)
    
    # Line thickness of -1 px
    # Thickness of -1 will fill the entire shape
    dim_factor = (img.shape[0] + img.shape[1]) / 2

    thickness = int(dim_factor / DIV_FACTOR)
    
    for bb in bboxes:

        x1 = int(bb[0])
        y1 = int(bb[1])
        x2 = int(bb[2])
        y2 = int(bb[3])

        # Start coordinate, here (100, 50)
        # represents the top left corner of rectangle
        start_point = (x1, y1)
    
        # Ending coordinate, here (125, 80)
        # represents the bottom right corner of rectangle
        end_point = (x2, y2)
    
        # Using cv2.rectangle() method
        # Draw a rectangle of black color of thickness -1 px
        img_bb = cv2.rectangle(img, start_point, end_point, color, thickness)

        # Save img
        cv2.imwrite(join(settings.DETECTED_FOLDER, img_name), img_bb)


def draw_mask(pred_data, img_name, mask_alpha: float):
    """
    Draw colored mask and save the image.
    """

    # Load image
    img = cv2.imread(join(settings.UPLOAD_FOLDER, img_name))
    img_h = img.shape[0]
    img_w = img.shape[1]

    # Create heatmaps
    heatmaps = create_heatmaps(img_h, img_w, pred_data)

    # Create mask
    mask = create_mask(img_h, img_w, heatmaps, mask_alpha)

    # Combine images
    add_transparent_image(img, mask, 0, 0)  # 0, 0 means no offset

    # Save img
    cv2.imwrite(join(settings.DETECTED_FOLDER, img_name), img)


def create_heatmaps(height, width, bbs):
    # Create one heatmap for each class
    heatmap = np.zeros((height, width))
    heatmap_obj = np.zeros((height, width))
    heatmap_no_obj = np.zeros((height, width))

    for bb in bbs:

        cls = int(bb[5])

        x1 = int(bb[0])
        y1 = int(bb[1])
        x2 = int(bb[2])
        y2 = int(bb[3])

        if cls == 0:
            heatmap_obj[y1:y2, x1:x2] = 1.
        elif cls == 1:
            heatmap_no_obj[y1:y2, x1:x2] = 1. 
    
        heatmap[y1:y2, x1:x2] = 1.
    
    if heatmap.any():
        heatmap = scale_range(heatmap) #, 0, 255)

    if heatmap_obj.any():
        heatmap_obj = scale_range(heatmap_obj) #, 0, 255)

    if heatmap_no_obj.any():
        heatmap_no_obj = scale_range(heatmap_no_obj) #, 0, 255)

    return heatmap, heatmap_obj, heatmap_no_obj


# def scale_range(array, out_min, out_max):
#     array += -(np.min(array))
#     array /= np.max(array) / (out_max - out_min)
#     array += out_min
#     array = array.astype(np.int64)
    
#     return array

def scale_range(array):
    array = np.interp(array, (array.min(), array.max()), (0, 255))
    array = array.astype(np.int64)
    return array


def create_mask(height, width, heatmaps: tuple, mask_alpha):
    heatmap, heatmap_obj, heatmap_no_obj = heatmaps

    # Build unique mask

    b = np.zeros((height, width)).astype(np.float32)
    g = heatmap_obj.copy().astype(np.float32)
    r = heatmap_no_obj.copy().astype(np.float32)

    # if not heatmap_obj.any():
    #     g = np.ones((height, width)).astype(np.float32)
    # else:
    #     g = heatmap_obj.copy().astype(np.float32)
    
    # if not heatmap_no_obj.any():
    #     r = np.ones((height, width)).astype(np.float32)
    # else:
    #     r = heatmap_no_obj.copy().astype(np.float32)

    alpha = heatmap.copy().astype(np.float32) * mask_alpha
    rgba = [b, g, r, alpha]
    mask = cv2.merge(rgba, 4)
    mask_blur = cv2.GaussianBlur(mask, ksize=(51, 51), sigmaX=20, borderType=cv2.BORDER_DEFAULT)

    return mask_blur


def add_transparent_image(background, foreground, x_offset=None, y_offset=None):
    """
    Adds a RGB background image with an RGBA foreground image.
    """
    bg_h, bg_w, bg_channels = background.shape
    fg_h, fg_w, fg_channels = foreground.shape

    assert bg_channels == 3, f'background image should have exactly 3 channels (RGB). found:{bg_channels}'
    assert fg_channels == 4, f'foreground image should have exactly 4 channels (RGBA). found:{fg_channels}'

    # center by default
    if x_offset is None: x_offset = (bg_w - fg_w) // 2
    if y_offset is None: y_offset = (bg_h - fg_h) // 2

    w = min(fg_w, bg_w, fg_w + x_offset, bg_w - x_offset)
    h = min(fg_h, bg_h, fg_h + y_offset, bg_h - y_offset)

    if w < 1 or h < 1: return

    # clip foreground and background images to the overlapping regions
    bg_x = max(0, x_offset)
    bg_y = max(0, y_offset)
    fg_x = max(0, x_offset * -1)
    fg_y = max(0, y_offset * -1)
    foreground = foreground[fg_y:fg_y + h, fg_x:fg_x + w]
    background_subsection = background[bg_y:bg_y + h, bg_x:bg_x + w]

    # separate alpha and color channels from the foreground image
    foreground_colors = foreground[:, :, :3]
    alpha_channel = foreground[:, :, 3] / 255  # 0-255 => 0.0-1.0

    # construct an alpha_mask that matches the image shape
    alpha_mask = np.dstack((alpha_channel, alpha_channel, alpha_channel))

    # combine the background with the overlay image weighted by alpha
    composite = background_subsection * (1 - alpha_mask) + foreground_colors * alpha_mask

    # overwrite the section of the background image that has been updated
    background[bg_y:bg_y + h, bg_x:bg_x + w] = composite


def verify_image(image_path):
    try:
        img = Image.open(image_path)
        img.verify()
        value = True
    except:
        value = False
    return value