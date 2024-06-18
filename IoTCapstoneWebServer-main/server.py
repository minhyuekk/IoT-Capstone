from flask import Flask, request, render_template, make_response
import os
import csv

app = Flask(__name__)
IMAGE_UPLOAD_FOLDER = 'static/pics'
CSV_UPLOAD_FOLDER = 'static/data'

# Ensure the upload folders exist
os.makedirs(IMAGE_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CSV_UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files or 'csv_data' not in request.form:
        return 'Missing image or csv_data part', 400

    image = request.files['image']
    csv_data = request.form['csv_data']
    csv_filename = request.form['csv_filename']

    if image.filename == '':
        return 'No selected image', 400

    if image:
        # Save image
        image_save_path = os.path.join(IMAGE_UPLOAD_FOLDER, image.filename)
        image.save(image_save_path)

        # Append CSV data
        csv_save_path = os.path.join(CSV_UPLOAD_FOLDER, csv_filename)
        with open(csv_save_path, 'a', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(csv_data.split(','))

        return 'Files uploaded and CSV data appended successfully', 200

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
