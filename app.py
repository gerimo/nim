import os
from flask import Flask, redirect, url_for, request, render_template, send_from_directory
from pymongo import MongoClient
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['pdf','mp3', 'mp3', '3ge', 'wev', 'flac', 'mov'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = MongoClient(
    'mongo',
    27017)
db = client.tododb

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/demo')
def demo():
    return render_template('demo.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS    

@app.route('/call_list', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template('call_list.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/todo')
def todo():
    _items = db.tododb.find()
    items = [item for item in _items]
    return render_template('todo.html', items=items)

@app.route('/new', methods=['POST'])
def new():
    item_doc = {
        'name': request.form['name'],
        'description': request.form['description']
    }
    db.tododb.insert_one(item_doc)
    return redirect(url_for('todo'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
