import os
import weights

# We will store images uploaded by the user on this folder
UPLOAD_FOLDER = "uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# We will store images with detections on this folder
DETECTED_FOLDER = "detections/"
os.makedirs(DETECTED_FOLDER, exist_ok=True)

WEIGHTS_FOLDER = "import/"
os.makedirs(WEIGHTS_FOLDER, exist_ok=True)

WEIGHTS_PATH = os.path.join(WEIGHTS_FOLDER, 'best.pt')
if not os.path.isfile(WEIGHTS_PATH):
    ONEDRIVE_LINK = "https://1drv.ms/u/s!AnDEqlL6-enzhct_GTjijAFvpQIQcQ?e=3OKLhJ"
    weights.from_onedrive(WEIGHTS_PATH, ONEDRIVE_LINK)


# REDIS
# Queue name
REDIS_QUEUE = 'job_queue'
# Port
REDIS_PORT = 6379
# DB Id
REDIS_DB_ID = 0
# Host IP
REDIS_IP = 'redis'
# Sleep parameters which manages the
# interval between requests to our redis queue
SERVER_SLEEP = 0.05