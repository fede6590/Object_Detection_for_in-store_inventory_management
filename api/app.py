import settings
import flask_login
import utils
import os

from flask import Flask
from flask_httpauth import HTTPTokenAuth
from middleware import model_detect

from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = settings.UPLOAD_FOLDER
app.config["DETECTED_FOLDER"] = settings.DETECTED_FOLDER
app.secret_key = "secret key"

# Login Manager
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

auth = HTTPTokenAuth(scheme='Bearer')

# Define user model
class User(flask_login.UserMixin):
    def __init__(self, id, name):
        self.id = id
        self.name = name        


@login_manager.user_loader
def user_loader(token):
    if token not in settings.TOKENS:
        return

    user = User(token, settings.TOKENS[token])
    return user


@login_manager.request_loader
def request_loader(request):
    token = request.form.get('token')
    if token not in settings.TOKENS:
        return

    user = User(token, settings.TOKENS[token])
    return user


@auth.verify_token
def verify_token(token):
    if token in settings.TOKENS:
        return settings.TOKENS[token]


# Views
@app.route("/", methods=["GET"])
def index():
    """
    Index endpoint, renders our HTML code.
    """
    if flask_login.current_user.is_authenticated:
        return render_template("index.html", name=flask_login.current_user.name)
    else:
        return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():    
    token = request.form['token']

    if token in settings.TOKENS:
        user = User(token, settings.TOKENS[token])
        flask_login.login_user(user)

        return redirect(url_for('index'))
    else:
        flash("Invalid Token!")

        return redirect(url_for('index'))


@app.route("/", methods=["POST"])
@flask_login.login_required
def upload_image():
    """
    Function used in our frontend so we can upload and show an image.
    When it receives an image from the UI, it also calls our ML model to
    get and display the detections.
    """
    # No file received, show basic UI
    if "file" not in request.files:
        flash("No file part")
        return redirect(request.url)

    # File received but no filename is provided, show basic UI
    file = request.files["file"]
    if file.filename == "":
        flash("No image selected for uploading")
        return redirect(request.url)

    
    # File received and it's an image, we must show it and get detections
    if file and utils.allowed_file(file.filename):

        hash_imgname = utils.get_file_hash(file)
        img_savepath = os.path.join(settings.UPLOAD_FOLDER, hash_imgname)

        if not os.path.exists(img_savepath):  # Check if the img already exist
            file.stream.seek(0)
            file.save(img_savepath)
            
            if not utils.verify_image(img_savepath):  # Check corruption
                os.remove(img_savepath)
                flash("Image is corrupted, try with another one")
                return redirect(request.url)

        pred_data = model_detect(hash_imgname)
        
        alpha = 0.5
        utils.draw_mask(pred_data, hash_imgname, alpha)  # Save the masked image

        return render_template("index.html", filename=hash_imgname, name=flask_login.current_user.name)

    # File received and but it isn't an image
    else:
        flash("Allowed image types are: PNG, JPG, JPEG, GIF")
        return redirect(request.url)


@app.route("/display_uploaded/<filename>")
def display_uploaded_image(filename):
    """
    Display uploaded image in our UI.
    """
    
    return redirect(url_for("static", filename="uploads/" + filename), code=301)


@app.route("/display_detected/<filename>")
def display_detected_image(filename):
    """
    Display detected image in our UI.
    """

    return redirect(url_for("static", filename="detections/" + filename), code=301)


@app.route('/logout', methods=["POST"])
def logout():
    flask_login.logout_user()
    return redirect(url_for('index'))


@app.route("/detect", methods=["POST"])
@auth.login_required
def detect():
    """
    Endpoint used to get detections without need to access the UI.
    Parameters
    ----------
    file : str
        Input image we want to get detections from.
    Returns
    -------
    flask.Response
        JSON response from our API having the following format:
            {
                "success": bool,
                "detections": list of bounding boxes
            }
        - "success" will be True if the input file is valid and we get 
        detections from our ML model.
        - "detections" model detections as a list of bounding boxes coordinates
    """
    if "file" not in request.files:
        rpse = {"success": False, "detections": None}
        return jsonify(rpse), 400

    # File received but no filename is provided
    file = request.files["file"]
    if file.filename == "":
        rpse = {"success": False, "detections": None}
        return jsonify(rpse), 400

    # File received and it's an image, we must show it and get predictions
    if file and utils.allowed_file(file.filename):
        hash_imgname = utils.get_file_hash(file)
        img_savepath = os.path.join(settings.UPLOAD_FOLDER, hash_imgname)
        
        if not os.path.exists(img_savepath):  # Check if the img already exist
            file.stream.seek(0)
            file.save(img_savepath)

            if not utils.verify_image(img_savepath):  # Check corruption
                os.remove(img_savepath)
                rpse = {"success": False, "detections": None}
                return jsonify(rpse), 400

        pred_data = model_detect(hash_imgname)

        detection_dict = {'User': auth.current_user(), 'Data:': pred_data}

        rpse = {"success": True, "detections": detection_dict}
        return jsonify(rpse), 200
    else:
        rpse = {"success": False, "detections": None}
        return jsonify(rpse), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=settings.API_DEBUG)