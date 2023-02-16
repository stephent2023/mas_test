from flask import Flask, render_template, request, send_file,redirect,url_for, Response, redirect

app = Flask(__name__)
api = Api(app)

@app.route("/")
def pagehome():
    return "<h1>Hello world<h1>"

if __name__=="__main__":
    app.run(port=8080)
