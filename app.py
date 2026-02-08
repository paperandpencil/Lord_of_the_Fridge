import os
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    send_from_directory,
    redirect,
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["TEST_SECRET"] = os.environ.get("TEST_SECRET")

# define directory where uploaded files (should only be ALLOWED images!) are stored
# IMAGE_DIR = os.path.join('static', 'images') # static/images
UPLOAD_FOLDER = "static/images"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}  # NOTE. this is a set, NOT a dict!
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# create folder if it does NOT exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
# v1 / sanity check
# def hello_world():
# 	return "<p>Hello, World!</p>"
def index():
    print(f"The secret key is: {app.config['TEST_SECRET']}")  # testing

    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # sanitize!
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return redirect(url_for("index"))

    # list images for gallery
    image_files = os.listdir(UPLOAD_FOLDER)  # list contents in UPLOAD_FOLDER
    images = [f for f in image_files if f.endswith((".png", ".jpg", ".jpeg", ".gif"))]
    return render_template("gallery.html", images=images)
    # TO DO, how to order the display of uploaded images, such that latest first?


if __name__ == "__main__":
    app.run(debug=True)
