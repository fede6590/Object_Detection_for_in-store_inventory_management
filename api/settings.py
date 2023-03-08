import os

# Run API in Debug mode
API_DEBUG = True

# We will store images uploaded by the user on this folder
UPLOAD_FOLDER = "static/uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# We will store images with detections on this folder
DETECTED_FOLDER = "static/detections/"
os.makedirs(DETECTED_FOLDER, exist_ok=True)

TOKENS = {
    "secret-token-1-abelardo": "Abe",
    "secret-token-2-alfredo": "Alfredo",
    "secret-token-3-federico": "Fede",
    "secret-token-4-jose": "Jose",
    "secret-token-5-gaston": "Gaston"
}

# REDIS settings
# Queue name
REDIS_QUEUE = "job_queue"
# Port
REDIS_PORT = 6379
# DB Id
REDIS_DB_ID = 0
# Host IP
REDIS_IP = "redis"
# Sleep parameters which manages the
# interval between requests to our redis queue
API_SLEEP = 0.05
