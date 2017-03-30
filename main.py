import os
from flask import Flask, redirect, url_for, request, render_template
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongo', 27017, connect=False)
db = client.default

@app.route('/call_list')
def call_list():
    return render_template('call_list.html')

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/todo')
def todo():
    _items = db.default.find()
    items = [item for item in _items]
    return render_template('todo.html', items=items)

@app.route('/new', methods=['POST'])
def new():
    item_doc = {
        'name': request.form['name'],
        'description': request.form['description']
    }
    db.default.insert_one(item_doc)
    return redirect(url_for('todo'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=80)