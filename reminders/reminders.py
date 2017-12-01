import os
import sqlite3
from flask import Flask, g, request, redirect, url_for

app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path,'reminders.db'),
    DEBUG=True
))

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

@app.route('/')
def hello_world():
    db = get_db()
    query = db.execute('select phone_number,reminder_text,reminder_time from reminders')
    reminders = query.fetchall()
    print reminders
    return str([str(r) for r in reminders])

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
