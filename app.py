import os, shutil
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    send_from_directory,
    redirect,
)
from werkzeug.utils import secure_filename
from PIL import Image

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


def is_valid_image(file):
    """Uses Pillow module to verify if a fileStorage object from flask request.files, is a valid image. If it is, then save to upload folder"""
    try:
        # determine if file is broken w/o actually decoding the data
        # if file is broken, then raise exception
        with Image.open(file.stream) as img:
            img.verify()

        # try to load data fully, to verify integrity
        # if problem, then raise exception
        with Image.open(file.stream) as img:
            img.load()
            if img.format not in ["JPEG", "PNG", "BMP", "GIF", "WEBP"]:
                return redirect(url_for("index"))

        filename = secure_filename(file.filename)  # sanitize! but why ???

        # using the uploaded file's filename as-is, is a temporary situation
        # todo, rename filename to timestamp_42intraLogin, to enable sorting for display
        # answers 2 questions:
        # (1) when was the item was deposited into the fridge, (2) by who

        with Image.open(file.stream) as img:
            # img.thumbnail((200, 200)) # resize to minimize space taken up by uploaded images?

            # only saves the first frame! so animated gifs etc. will "fail" to animate...
            img.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return redirect(url_for("index"))
    except (IOError, SyntaxError, FileNotFoundError) as e:
        print(f"Invalid image or file error: {e}")
        return redirect(url_for("index"))
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return redirect(url_for("index"))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:  # no file part
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":  # no selected file
            return redirect(request.url)
        is_valid_image(file)
        # Note "file" is a FileStorage object from request.files
        # has attributes/methods: .filename, .stream, .save(path)

    # if GET, then just list images for gallery
    image_files = os.listdir(UPLOAD_FOLDER)  # list contents in UPLOAD_FOLDER
    images = [
        f for f in image_files if f.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
    ]
    return render_template("gallery.html", images=images)
    # TO DO, how to order the display of uploaded images, such that latest first?


if __name__ == "__main__":
    app.run(debug=True)
