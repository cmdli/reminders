import os, time, sqlite3
from flask import Flask, g, request, redirect, url_for
from twilio.rest import Client as TwilioClient
from twilio.twiml.messaging_response import MessagingResponse, Message

######## App Setup

def install_secret_config(app):
    filepath = os.path.join(app.root_path,'secret.cfg')
    print "Secret Config:"
    try:
        lines = open(filepath, 'r').readlines()
        for line in lines:
            line = line.strip()
            key,value = line.split("=")[:2]
            app.config[key] = value
            print "Adding " + key + ":" + value
    except ValueError:
        print "Secret config has syntax error"
    except IOError:
        print "Could not load secret config at secret.cfg!"

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
def get_reminders():
    db = get_db()
    cursor = db.execute('select * from reminders')
    reminders = cursor.fetchall()
    return str([tuple(r) for r in reminders])

@app.route('/add', methods=['POST'])
def add():
    add_reminder(request.form['number'],
                request.form['text'],
                request.form['time'])
    return redirect(url_for('get_reminders'))

def usage():
    resp = MessagingResponse()
    resp.message("Sorry, didn't catch that. Usage: <text> <time from now>")
    return str(resp)

@app.route('/receive', methods=['POST'])
def receive():
    try:
        # Body form - <text> <# of seconds from now>
        body = request.values['Body']
        number = request.values['From']
        values = body.split(' ')
        text,expiration = values[0],int(values[1])
        reminder_time = expiration + int(time.time()) # Add current time
        add_reminder(number,text,reminder_time)
        resp = MessagingResponse()
        resp.message("Added reminder for '" + text +
                     "' in " + str(expiration) + " seconds")
        return str(resp)
    except (ValueError,KeyError,IndexError):
        return usage()

def add_reminder(number,body,time):
    db = get_db()
    db.execute('insert into reminders (phone_number,reminder_text,reminder_time)'
               + ' values (?,?,?)', [number,body,time])
    db.commit()

@app.route('/send_reminders', methods=['GET'])
def send_reminders():
    db = get_db()
    cursor = db.execute('select * from reminders')
    reminders = cursor.fetchall()
    client = TwilioClient(app.config['TWILIO_SID'],app.config['TWILIO_AUTH_TOKEN'])
    sent = []
    current = int(time.time())
    for reminder in reminders:
        if reminder['reminder_time'] < current:
            client.api.account.messages.create(
                to=reminder['phone_number'],
                from_=app.config['TWILIO_NUMBER'],
                body=reminder['reminder_text']
            )
            sent.append(reminder)
    for reminder in sent:
        db.execute('delete from reminders where id=(?)', [reminder['id']])
    db.commit()
    return str([tuple(r) for r in sent])

@app.route('/send', methods=['POST'])
def send():
    send_message(request.form['number'], request.form['body'])
    return "Done."

def send_message(to,body):
    client = TwilioClient(app.config['TWILIO_SID'],app.config['TWILIO_AUTH_TOKEN'])
    client.api.account.messages.create(
        to=to,
        from_=app.config['TWILIO_NUMBER'],
        body=body
    )

if __name__ == "__main__":
    app.run()
