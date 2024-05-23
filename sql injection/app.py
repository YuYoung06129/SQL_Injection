import re
from flask import Flask, request, render_template, g, session, redirect
import sqlite3
import os
import binascii

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = "./static/database.db"
if not os.path.exists(DATABASE):
    db = sqlite3.connect(DATABASE)
    db.execute('create table users(uid text, upw text);')
    db.execute(f'insert into users(uid, upw) values ("guest", "guest"), ("admin", "{binascii.hexlify(os.urandom(16)).decode("utf8")}");')
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

keywords = ['union', 'select', 'from', 'and', 'or', '*', '/', 'like', '()', '|', '&']
def check_WAF(data):
    for keyword in keywords:
        if keyword in data:
            return True

    return False


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if session:
        return redirect('/main_page')
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        uid = request.form.get('uid')
        upw = request.form.get('upw')
        if check_WAF(uid + upw):
            return f'<h1> Be blocked by the WAF </h1>'
        query = f'SELECT * FROM users WHERE uid="{uid}" AND upw={upw}'
        res = query_db(query)
        if res:
            uid = res['uid']
            if uid == 'admin':
                return render_template("flag.html")
            return f"<h1>It's not admin It's {uid}</h1>"
        return render_template('fishing.html')

if __name__ == '__main__':
    app.run(port=8000, debug=True)