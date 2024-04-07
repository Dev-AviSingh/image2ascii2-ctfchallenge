from flask import Flask, request, jsonify, render_template, render_template_string, send_from_directory
from PIL import Image
import traceback
import os
from datetime import datetime
from typing import TypedDict
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from threading import Thread
app = Flask(__name__)
app.secret_key = r"0ctf{XSS_w1th_extra_st3ps}"
# Define ASCII characters for different luminance levels
ASCII_CHARS = r'''@&%QWNM0gB$#DR8mHXKAUbGOpV4d9h6PkqwSE2]ayjxY5Zoen[ult13If}C{iF|(7J)vTLs?z/*cr!+<>;=^,_:'-.`'''
URL, PORT = "0.0.0.0", 5000
class AsciiArt(TypedDict):
    ascii:str
    imageName:str

if not os.path.exists("original_images"):
    os.mkdir("original_images")

asciiArts:list[AsciiArt] = []

with open("error_log.txt", "w") as f:
    f.write("Errors : \n")

# Function to convert a pixel to ASCII character
def pixel_to_ascii(pixel_value, ascii_chars):
    index = int(pixel_value * (len(ascii_chars) / 256.0))
    return ascii_chars[index]

# Function to convert an image to ASCII art
def image_to_ascii(image_path, output_width=100, ascii_chars=ASCII_CHARS):
    try:
        image = Image.open(image_path)
        aspect_ratio = image.height / image.width
        new_height = int(output_width * aspect_ratio)
        resized_image = image.resize((output_width, new_height))
        grayscale_image = resized_image.convert("L")
        pixels = grayscale_image.getdata()
        ascii_characters = [pixel_to_ascii(pixel, ascii_chars) for pixel in pixels]
        ascii_art = [ascii_characters[i:i + output_width] for i in range(0, len(ascii_characters), output_width)]
        ascii_art = [" ".join(row) for row in ascii_art]
        ascii_art = "\n".join(ascii_art)
        return ascii_art

    except Exception as e:
        log_message = "Exception: {}\nFile: {}\nAction: Not Allowed".format(str(e), image_path)
        with open("error_log.txt", "a") as log_file:
            log_file.write(log_message + "\n")
        raise


def runBot():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    print("Bot started.")
    driver.get("http://127.0.0.1:5000/")
    driver.add_cookie({"name":"flag", "value":str(app.secret_key)})
    

    button = driver.find_element(By.ID, "refreshButton")
    button.click()
    driver.implicitly_wait(5)
    driver.close()
    print("Bot closed.")


@app.route('/convert', methods=['POST'])
def convert_image():
    # print(request.form)
    # print(request.files)
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        allowed_extensions = {'jpg', 'jpeg', 'png', }
        if '.' in image_file.filename and image_file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            errorMsg = f"<b>File format not supported {datetime.now().strftime(r'%d/%m/%Y %H:%M:%S')}: {image_file.filename} </b>\n"
            with open("error_log.txt", "a") as f:
                f.write(errorMsg)
            return jsonify({"error": f"Unsupported file format. Only {', '.join(allowed_extensions)} allowed."}), 400

        # Save the uploaded image    to a temporary file
        imagePath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "original_images",
            image_file.filename)
        print(f"Saved at {imagePath}")
        image_file.save(imagePath)

        # Convert the image to ASCII art
        ascii_art = image_to_ascii(imagePath)
        asciiArts.append(AsciiArt(ascii = ascii_art, imageName = image_file.filename))

        Thread(target = runBot).start()
        return jsonify({"status":"Successfully Converted"})

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route("/originalImage/<path:filepath>")
def getOriginalImage(filepath):
    return send_from_directory("original_images", filepath)

@app.route("/getAsciiArts")
def getAsciiArts():
    return jsonify(asciiArts)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host = URL, port= PORT, debug=True)
