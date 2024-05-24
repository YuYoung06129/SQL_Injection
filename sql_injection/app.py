#!/usr/bin/python3
from flask import Flask, request, render_template, g
import sqlite3
import os
import binascii

app = Flask(__name__)
app.secret_key = os.urandom(32)

try:
    FLAG = open('./flag.txt', 'r').read()
except:
    FLAG = '[**FLAG**]'

DATABASE = "database.db"
if os.path.exists(DATABASE) == False:
    db = sqlite3.connect(DATABASE)
    db.execute('CREATE TABLE users(uid char(100), upw char(100));')
    db.execute(f'INSERT INTO users(uid, upw) VALUES ("test", "test"), ("admin", "{binascii.hexlify(os.urandom(16)).decode("utf8")}");')
    db.commit()
    db.close()



def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def query_db(query, one=True):
    cur = get_db().execute(query)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

keywords = ['union', 'select', 'from', 'and', 'or', '*', '/', 'like', '()', '|', '&', 'admin', '0x']
def check_WAF(data):
    for keyword in keywords:
        if keyword in data:
            return True

    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        uid = request.form.get('uid')
        upw = request.form.get('upw')
        if check_WAF(uid + upw):
            return f'<h1> Be blocked by the WAF </h1>'
        res = query_db(f'SELECT * FROM users WHERE uid="{uid}" and upw="{upw}"')
        if res:
            uid = res[0]
            if uid == 'admin':
                return render_template('flag.html')
            return f"You're not admin, It's {uid}"
        return '<h1>땡!</h1>'

app.run(host='0.0.0.0', port=8000)
