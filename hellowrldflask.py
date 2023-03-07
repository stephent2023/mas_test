from flask import Flask
import os

app = Flask(__name__)

print(os.environ)
print("cool")

@app.route("/")
def pagehome():
    return "<h1>Hello world<h1>"

if __name__=="__main__":
    app.run(host="0.0.0.0",port=8001)
