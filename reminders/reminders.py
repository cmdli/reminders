
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<!DOCTYPE html><html><body>Hello world!</body></html>"

if __name__ == "__main__":
    app.run()
