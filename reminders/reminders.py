import os
import sqlite3
from flask import Flask, g, request, redirect, url_for

######## App Setup

def install_secret_config(app):
    filepath = os.path.join(app.root_path,'secret.cfg')
    print "Secret Config:"
    try:
        lines = open(filepath, 'r').readlines()
        for line in lines:
            key,value = line.split("=")[:2]
            app.config[key] = value
            print "Adding " + key + ":" + value
    except ValueError:
        print "Secret config has syntax error"
    except IOError:
        print "Could not load secret config!"

app = Flask(__name__)
install_secret_config(app)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path,'reminders.db'),
    DEBUG=True
))

####### Database

def connect_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

######## Requests
        
@app.route('/')
def hello_world():
    db = get_db()
    cursor = db.execute('select phone_number,reminder_text,reminder_time from reminders')
    reminders = cursor.fetchall()
    return str([tuple(r) for r in reminders])

@app.route('/add', methods=['POST'])
def add():
    db = get_db()
    db.execute('insert into reminders (phone_number,reminder_text,reminder_time)' +
               'values (?,?,?)',
               [request.form['number'],request.form['text'],request.form['time']])
    db.commit()
    return redirect(url_for('hello_world'))



if __name__ == "__main__":
    app.run()
