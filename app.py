from flask import Flask, render_template, request, redirect, session, send_file
from flask_session import Session
import tempfile
import sys

from prompt_gen import get_labels_from_image_url, generate_prompt_from_labels
from google_drive_api import upload_prompt, list_files_in_folder, wait_for_file_and_download
from spotify_api import retrieve_playlists, retrieve_image_urls, retrieve_playlist_info, upload_to_spotify
from image_gen import generate_image
import time

# create flask app
app = Flask(__name__)


# configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# encountered issue with using Session() on google cloud, troubleshooted with AI (Chat-GPT 3 May 2025)
# directed to tempfile and Flask_Session docs

app.config['SESSION_FILE_DIR'] = tempfile.gettempdir() # (tempfile/Flask_Session docs 3 May 2025)

# initiate session
Session(app)

# set up Spotify Web App API credentials (Spotify API docs 15 May 2025)
CLIENT_ID = "9b3abac0b22b4a34bb1b7069434bc837"
CLIENT_SECRET = "c6af27065a944c389bf202af6a15ad41"
scope = "ugc-image-upload playlist-modify-public playlist-modify-private playlist-read-private user-read-private user-read-email"
REDIRECT_URI = "https://playlist-cover-image-gen.uw.r.appspot.com/callback"

timeout = 180
# Test with command line: python app.py 1
if len(sys.argv) == 2 and sys.argv[1] == '1':
    REDIRECT_URI = "http://127.0.0.1:5000/callback"
    timeout = 5

# define home route with decorator
@app.route("/")
def index():

    # display index template - see index.html
    return render_template("index.html")

# define login route with decorator
@app.route("/login")
def login():
    # piece together Spotify API authorization link (Spotify API docs 15 May 2025)
    query_string = f'response_type=code&client_id={CLIENT_ID}&scope={scope}&redirect_uri={REDIRECT_URI}'
    auth_url = f'https://accounts.spotify.com/authorize?{query_string}'

    # redirect user to Spotify login page for authentification
    return redirect(auth_url)

# define callback route - where Spotify authentication page routes to after successful login (Spotify API docs 15 May 2025)
@app.route("/callback", methods = ["GET", "POST"])
def callback():
    # retrieve authorization code from Spotify API authentication and error if applicable
    code = request.args.get("code")
    error = request.args.get("error")

    # error handling
    if error:
        return render_template("error.html")
    if not code:
        return render_template("error.html")

    # get access token, a dictionary containing a user's playlist info, and the user's id - see spotify_api.py
    access_token, playlists_info, user_id = retrieve_playlists(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, code)

    # set access_token as a session variable to use in other routes
    session["access_token"] = access_token

    session["user_id"] = user_id

    # render page that prompts user to select a playlist - see authorized.html
    return render_template("authorized.html", playlists_info=playlists_info, user_id=user_id)

# define image_gen route with decorator
@app.route("/image_gen", methods = ["GET", "POST"])
def image_gen():
    print("Image generation process beginning\n")
    t = time

    print("Fetching playlist info...\n")

    # get playlist_id from GET request
    playlist_id = request.args.get("selected_playlist_id")
    # get access token from session
    access_token = session.get("access_token")

    # store playlist_id in session
    session["playlist_id"] = playlist_id

    # retrieve song data from selected_playlist - see spotify_api.py
    song_info = retrieve_playlist_info(access_token, playlist_id)

    # get image urls from song info - see spotify_api.py
    image_urls = retrieve_image_urls(song_info)

    # generate image labels from urls - see prompt_gen.py
    song_labels = get_labels_from_image_url(image_urls)

    print("Generating prompt...\n")

    # generate AI prompts from image labels - see prompt_gen.py
    prompt = generate_prompt_from_labels(song_labels)

    # store prompt
    session["prompt"] = prompt


    print("Generating image...\n")
    start_time = time.perf_counter()

    # generate the image
    image_success = generate_image(prompt)

    end_time = time.perf_counter()

    time_to_generate = end_time - start_time

    print(f"Done! Image took {time_to_generate:.4f} seconds to generate\n")

    return redirect("/results")

# define results route with decorator
@app.route("/results", methods = ["POST", "GET"])
def results():
    # get prompt from session
    prompt = session.get("prompt")

    # render results template - see results.html
    return render_template("results.html", prompt=prompt, image_url="/tmp/output.png")

# define results route with decorator
@app.route("/final_results", methods=["POST"])
def final_results():
    # find if upload image box was checked via PUT request
    if request.form.get("upload") == "true":

        # get session variables
        playlist_id = session.get("playlist_id")
        access_token = session.get('access_token')

        # upload image to spotfiy playlist - see spotify_api.py
        response = upload_to_spotify(access_token, playlist_id)

        # logic to render results template based on response code - see results.html
        if response.status_code == 202:
            return render_template("results.html", prompt=session.get("prompt"), image_url="/tmp/output.png", message="Successfully uploaded to Spotify!")
        else:
            return render_template("results.html", image_url="/tmp/output.png", message="Failed: Error code" + response.status_code + response.text)

    # re-render results template unchanged if upload not chosen
    return render_template("results.html", prompt=prompt, image_path="/tmp/output.png")

# define output route with decorator 
@app.route('/output')
def output():
    # use send_file to return file from Flask server - needed due to temporary storage (send_file docs 3 Jun 2025)
    return send_file("/tmp/output.png", mimetype='image/png')

# run flask app
if __name__ == "__main__":
    app.run(debug=True)



