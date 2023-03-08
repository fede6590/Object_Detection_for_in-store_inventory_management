import time
import redis
import os
import settings
import json

from torch import hub

db = redis.Redis(
    host = settings.REDIS_IP,
    port = settings.REDIS_PORT,
    db = settings.REDIS_DB_ID
)

model = hub.load('./yolov5/', 'custom', path=settings.WEIGHTS_PATH, source='local', force_reload=True)

model.conf = 0.25  # NMS confidence threshold
model.iou = 0.25  # NMS IoU threshold
model.agnostic = True

def predict(image_name):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.

    Returns
    -------
    preds: lists of BBs coordinates, confidence and class. 
    """

    img = os.path.join(settings.UPLOAD_FOLDER, image_name)
    results = model(img)

    preds = results.xyxy[0].tolist()

    return preds
 

def detection_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """
    while True:
        _, job_data_str = db.brpop(settings.REDIS_QUEUE)
        job_data = json.loads(job_data_str)

        try:
            preds = predict(job_data["image_name"])
            pred_data = preds
            status = "detection_ok"
        except:
            pred_data = None
            status = "error"        

        job_result = {"pred_data": pred_data, "status": status}
        job_result_str = json.dumps(job_result)
        
        db.set(job_data["id"], job_result_str)

        # Don't forget to sleep for a bit at the end
        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    detection_process()
