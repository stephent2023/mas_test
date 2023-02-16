from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse
from flaskext.mysql import MySQL
from datetime import datetime, timedelta
import json

app = Flask(__name__)
api = Api(app)

mysql = MySQL(app)
app.config['MYSQL_DATABASE_USER'] = 'masteradmin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'H4br)+tU8m'
app.config['MYSQL_DATABASE_DB'] = 'Monitoring'
app.config['MYSQL_DATABASE_HOST'] = 'system.cjufabmrbwai.eu-west-2.rds.amazonaws.com'
app.config['MYSQL_DATABASE_PORT'] = 3306
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()

@app.route("/")
def pagehome():
    try:
        cursor.execute('INSERT INTO LoginEvents(Hostname,Username,Timestamp,Elapsed) VALUES ("Joe Weaver","Weaverbeaver","2008-11-11",1887)')
        conn.commit()
        cursor.close()
        return "<h1>Hello world<h1>"
    except:
        return render_template('frog.html')

@app.route("/LoginEvents")
def tableview():
    cursor.execute('SELECT * FROM LoginEvents')
    results = cursor.fetchall()
    return render_template('index.html', results=results)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=8080)