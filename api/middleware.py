import json
import redis
import settings
import uuid
import time


db = redis.Redis(
    host = settings.REDIS_IP, 
    port = settings.REDIS_PORT, 
    db = settings.REDIS_DB_ID
)


def model_detect(image_name):
    """
    Receives an image name and queues the job into Redis.
    Will loop until getting the answer from our ML service.

    Parameters
    ----------
    image_name : str
        Name of the image uploaded by the user.

    Returns
    -------
    pred_data : str
        Prediction data.
    """

    job_id = str(uuid.uuid4())

    job_data = {
        "id": job_id,
        "image_name": image_name,
    }

    job_data_str = json.dumps(job_data)

    db.rpush(settings.REDIS_QUEUE, job_data_str)

    # Loop until we received the response from our ML model
    while True:
        if db.exists(job_data["id"]):

            job_result_str = db.get(job_data["id"])
            job_result = json.loads(job_result_str)
            pred_data = job_result["pred_data"]

            if job_result["status"] == "detection_ok":
                db.delete(job_data["id"])
                break
            elif job_result["status"] == "error":
                # error: pred_data = None
                break

        time.sleep(settings.API_SLEEP)

    return pred_data
