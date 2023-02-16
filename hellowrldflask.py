from flask import Flask

app = Flask(__name__)
api = Api(app)

@app.route("/")
def pagehome():
    return "<h1>Hello world<h1>"

if __name__=="__main__":
    app.run(port=8080)