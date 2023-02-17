from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse
from flaskext.mysql import MySQL
from datetime import datetime, timedelta
import json

app = Flask(__name__)
api = Api(app)

mysql = MySQL(app)
app.config['MYSQL_DATABASE_USER'] = 'master'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Badminton!'
app.config['MYSQL_DATABASE_DB'] = 'monitoring'
app.config['MYSQL_DATABASE_HOST'] = 'grafanards.crgp9ayzq9mq.eu-west-2.rds.amazonaws.com'
app.config['MYSQL_DATABASE_PORT'] = 3306
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()

@app.route("/")
def pagehome():
    try:
        cursor.execute('INSERT INTO LoginEvents(Hostname,Username,Timestamp,Elapsed) VALUES ("jweavoid","Weaverbeaver","2008-10-11",1990)')
        conn.commit()
        cursor.close()
        return "<h1>Hello world<h1>"
    except:
        return "<h1>Already there!!<h1>"

@app.route("/LoginEvents")
def tableview():
    cursor.execute('SELECT * FROM LoginEvents')
    results = cursor.fetchall()
    return "<h1>Selected!!<h1>"

if __name__=="__main__":
    app.run(port=8081)
