from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

def main(argv, db, fs):
    app.run()
