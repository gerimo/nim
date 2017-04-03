import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from flask import Flask, redirect, url_for, request, render_template, send_from_directory
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename

#The DB connection will assume that the database has the same name as the Flask Appliction which is "app"
app = Flask(__name__)
mongo = PyMongo(app)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['pdf','mp3', 'mp3', '3ge', 'wev', 'flac', 'mov'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    total = len(os.listdir('./uploads'))
    count = 0
    # generate list of available files already uploaded, to display on the view
    files = os.listdir('./uploads')
    # upload a new file to the view
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
    return render_template('call_list.html', count = count, total = total, files = files)

# retrieve the transcript
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

# view user prpfile        
@app.route('/user')
def user():
    user = mongo.db.users.find_one_or_404({'name': "Phonaroid.com"})
    return render_template('user.html',
        user=user)

@app.route('/new', methods=['POST'])
def new():
    item_doc = {
        'name': request.form['name'],
        'description': request.form['description']
    }
    db.tododb.insert_one(item_doc)
    return redirect(url_for('todo'))

# Para login de usuario
@app.route('/username')
def user_profile():
    user = mongo.db.users.find_one_or_404({'name': "Phonaroid.com"})
    return render_template('user.html',
        user=user)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
