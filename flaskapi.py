#Initialise libraries
from flask import Flask
from flask_restx import Api, Resource, reqparse
from flaskext.mysql import MySQL
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
api = Api(app)


#Configure DB connection
#DB info is pulled from secrets in the innershift environment
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = os.environ.get('DB_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ.get('DB_PASS')
app.config['MYSQL_DATABASE_DB'] = os.environ.get('DB_NAME')
app.config['MYSQL_DATABASE_HOST'] = os.environ.get('DB_ENDPOINT')
app.config['MYSQL_DATABASE_PORT'] = int(os.environ.get('DB_PORT'))

#Connect to the database
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()


#Defining API endpoints
#For endpoints that take arguements, args are defined first, then a route and a class


#####AddLoginEvent#####
#Adds login to LoginEvents
login_event_parse = reqparse.RequestParser()
login_event_parse.add_argument('hostname', type=str, help='Hostname of machine logged into')
login_event_parse.add_argument('username', type=str, help='Username of user logging on')
login_event_parse.add_argument('timestamp', type=int, help='Unix time of login event')
login_event_parse.add_argument('elapsed', type=str, help='Elapsed time of login')

@api.route("/AddLoginEvent")
class AddLoginEvent(Resource):
                @api.doc(parser=login_event_parse)
                def post(self):
                                try:
                                                args = login_event_parse.parse_args()
                                                hostname = args['hostname']
                                                username = args['username']
                                                timestamp = args['timestamp']
                                                elapsed = args['elapsed']
                                                if (elapsed):
                                                                sql = "INSERT INTO LoginEvents(Hostname,Username,Timestamp,Elapsed) VALUES('" + hostname + "', '" + username + "', FROM_UNIXTIME('" + str(timestamp) + "'),'" + str(elapsed) + "') ON DUPLICATE KEY UPDATE Hostname='" + hostname + "', Username='" + username + "', Timestamp=FROM_UNIXTIME('" + str(timestamp) + "'),Elapsed='" + str(elapsed) + "'"
                                                else:
                                                                sql = "INSERT INTO LoginEvents(Hostname,Username,Timestamp) VALUES('" + hostname + "', '" + username + "', FROM_UNIXTIME('" + str(timestamp) + "')) ON DUPLICATE KEY UPDATE Hostname='" + hostname + "', Username='" + username + "', Timestamp=FROM_UNIXTIME('" + str(timestamp) + "')"
                                                cursor.execute(sql)
                                                conn.commit()
                                                return {'Hostname': hostname, 'Username': username, 'Timestamp': str(timestamp), 'Elapsed': str(elapsed)}
                                except Exception as e:
                                                return {'error': str(e)}


#####AuditStats#####
#Returns number of devices that haven't check into SCCM Sophos or reported Audit data and desktops that haven;t been seen for 7 days
@api.route("/AuditStats")
class AuditStats(Resource):
                def post(self):
                                try:
                                                sql = "SELECT count(*) FROM AuditLastReported WHERE GREATEST(COALESCE(LastReported,0),COALESCE(Sophos,0)) - INTERVAL 2 DAY > SCCM AND SCCM IS NOT null AND ((Hostname LIKE '%DESKTOP%') OR (Hostname LIKE '%VDI%')) AND (SCCMupdated >= (SELECT MAX(SCCMupdated) FROM AuditLastReported WHERE Hostname LIKE '%DESKTOP%'))"
                                                cursor.execute(sql)
                                                NoSCCM = cursor.fetchall()
                                                sql = "SELECT count(*) FROM AuditLastReported WHERE LastReported < GREATEST(COALESCE(SCCM,0),COALESCE(Sophos,0)) - INTERVAL 3 DAY AND ((Hostname LIKE '%DESKTOP%') OR (Hostname LIKE '%VDI%')) AND (SCCMupdated >= (SELECT MAX(SCCMupdated) FROM AuditLastReported WHERE Hostname LIKE '%DESKTOP%'))"
                                                cursor.execute(sql)
                                                NoAudit = cursor.fetchall()
                                                sql = "SELECT COUNT(LastReported) FROM AuditLastReported WHERE (GREATEST(COALESCE(LastReported,0),COALESCE(SCCM,0),COALESCE(Sophos,0)) < NOW() - INTERVAL 7 DAY) AND ((Hostname NOT LIKE '%LAPTOP%') AND (Hostname NOT LIKE '%TABLET%')) AND (SCCMupdated >= (SELECT MAX(SCCMupdated) FROM AuditLastReported WHERE Hostname LIKE '%DESKTOP%'))"
                                                cursor.execute(sql)
                                                sevendays = cursor.fetchall()
                                                sql = "SELECT count(*) FROM AuditLastReported WHERE GREATEST(COALESCE(LastReported,0),COALESCE(SCCM,0)) > Sophos + INTERVAL 3 DAY AND ((Hostname LIKE '%DESKTOP%') OR (Hostname LIKE '%VDI%')) AND (SCCMupdated >= (SELECT MAX(SCCMupdated) FROM AuditLastReported WHERE Hostname LIKE '%DESKTOP%'))"
                                                cursor.execute(sql)
                                                NoSophos = cursor.fetchall()
                                                return {'NoSCCM': NoSCCM, 'NoAudit': NoAudit, 'unseen7days': sevendays, 'NoSophos': NoSophos}
                                except Exception as e:
                                                return {'error': str(e)}


#####DeviceStatus#####
#Returns the last time a given device check into Sophos, SSCM and Audit
device_status_args = reqparse.RequestParser()
device_status_args.add_argument('hostname', type=str, help='Hostname of machine to update')

@api.route("/DeviceStatus")
class DeviceStatus(Resource):
                @api.doc(parser=device_status_args)
                def post(self):
                                try:
                                                args = device_status_args.parse_args()
                                                hostname = args['hostname']
                                                sql = "SELECT LastReported FROM AuditLastReported WHERE Hostname LIKE '" + hostname + "%'"
                                                cursor.execute(sql)
                                                Audit = cursor.fetchall()
                                                sql = "SELECT SCCM FROM AuditLastReported WHERE Hostname LIKE '" + hostname + "%'"
                                                cursor.execute(sql)
                                                SCCM = cursor.fetchall()
                                                sql = "SELECT Sophos FROM AuditLastReported WHERE Hostname LIKE '" + hostname + "%'"
                                                cursor.execute(sql)
                                                Sophos = cursor.fetchall()
                                                return {'SCCM': str(SCCM[0][0]), 'Audit': str(Audit[0][0]), 'Sophos': str(Sophos[0][0])}
                                except Exception as e:
                                                return {'error': str(e)}


#####ListUserLogins#####
#Returns list of logins by a specified user since a specified date
list_logins_parse = reqparse.RequestParser()
list_logins_parse.add_argument('username', type=str, help='Username to list logins')
list_logins_parse.add_argument('fromdate', type=str, help='Date to search from (yyyymmdd)')

@api.route("/ListUserLogins")
class ListUserLogins(Resource):
                @api.doc(parser=list_logins_parse)
                def post(self):
                                try:
                                                args = list_logins_parse.parse_args()
                                                username = args['username']
                                                fromdate = args['fromdate']
                                                sql = "SELECT * FROM LoginEvents WHERE Username='" + username + "' AND Timestamp > '" + fromdate + "'"
                                                app.config['MYSQL_DATABASE_DB'] = 'Audit'
                                                cursor.execute(sql)
                                                data = cursor.fetchall()
                                                hashedData = {}
                                                returnedHTML = '<HTML><HEAD>Userdata</HEAD<BODY><TABLE>'
                                                for eachRow in data:
                                                                hashedData[str(eachRow[2])] = eachRow[0]
                                                                returnedHTML = returnedHTML + '<TR><TD>' + str(eachRow[2]) + '</TD><TD>' + eachRow[0] + '</TD></TR>'
                                                return hashedData
                                                returnedHTML = returnedHTML + '</TABLE></BODY></HTML>'
                                                response_headers = [
                                                                ('Content-Type', 'text/html'),
                                                                ('Content-Length', str(len(returnedHTML)))
                                                ]
#                                              start_response('200 OK', response_headers)
#                                              return returnedHTML
                                except Exception as e:
                                                return {'error': str(e)}


#####MobileDevices#####
#Returns number of mobile devices (laptops and tablets) not seen for 28 and 90 days
@api.route("/MobileDevices")
class MobileDevices(Resource):
                def post(self):
                                try:
                                                sql = "SELECT COUNT(LastReported) FROM AuditLastReported WHERE (LastReported < NOW() - INTERVAL 28 DAY) AND (SCCM < NOW() - INTERVAL 28 DAY) AND ((Hostname LIKE '%LAPTOP%') OR (Hostname LIKE '%TABLET%')) AND (SCCMupdated = (SELECT MAX(SCCMupdated) FROM AuditLastReported))"
                                                cursor.execute(sql)
                                                twentyeightdays = cursor.fetchall()
                                                sql = "SELECT COUNT(LastReported) FROM AuditLastReported WHERE (LastReported < NOW() - INTERVAL 90 DAY) AND (SCCM < NOW() - INTERVAL 90 DAY) AND ((Hostname LIKE '%LAPTOP%') OR (Hostname LIKE '%TABLET%')) AND (SCCMupdated = (SELECT MAX(SCCMupdated) FROM AuditLastReported))"
                                                cursor.execute(sql)
                                                ninetydays = cursor.fetchall()
                                                return {'28days': twentyeightdays, '90days': ninetydays}
                                except Exception as e:
                                                return {'error': str(e)}


#####NoAuditDevices#####
#Lists devices that have contacted SCCM or Sophos but havent reported audit data for 3 days split into mobile and static devices
@api.route("/NoAuditDevices")
class NoAuditDevices(Resource):
                def post(self):
                                try:
                                                sql = "SELECT SUBSTRING_INDEX(Hostname,'.',1),LastReported,SCCM,SCCMupdated,(SCCM - LastReported) FROM AuditLastReported WHERE LastReported < SCCM - INTERVAL 3 DAY AND ((Hostname LIKE '%DESKTOP%') OR (Hostname LIKE '%VDI%')) AND (SCCMupdated = (SELECT MAX(SCCMupdated) FROM AuditLastReported))"
                                                cursor.execute(sql)
                                                StaticDevices = cursor.fetchall()
                                                sql = "SELECT SUBSTRING_INDEX(Hostname,'.',1),LastReported,SCCM,SCCMupdated,(SCCM - LastReported) FROM AuditLastReported WHERE LastReported < SCCM - INTERVAL 3 DAY AND ((Hostname LIKE '%LAPTOP%') OR (Hostname LIKE '%TABLET%')) AND (SCCMupdated = (SELECT MAX(SCCMupdated) FROM AuditLastReported))"
                                                cursor.execute(sql)
                                                MobileDevices = cursor.fetchall()
                                                sql = "SELECT SUBSTRING_INDEX(Hostname,'.',1),LastReported,SCCM,SCCMupdated,(SCCM - LastReported) FROM AuditLastReported WHERE LastReported < SCCM - INTERVAL 3 DAY AND ((Hostname NOT LIKE '%LAPTOP%') AND (Hostname NOT LIKE '%TABLET%') AND (Hostname NOT LIKE '%DESKTOP%') AND (Hostname NOT LIKE '%VDI%')) AND (SCCMupdated = (SELECT MAX(SCCMupdated) FROM AuditLastReported))"
                                                cursor.execute(sql)
                                                OtherDevices = cursor.fetchall()
                                                hashedData = {}
                                                for eachRow in StaticDevices:
                                                                hashedData[str(eachRow[0])] = str(eachRow[1])
                                                for eachRow in MobileDevices:
                                                                hashedData[str(eachRow[0])] = str(eachRow[1])
                                                for eachRow in OtherDevices:
                                                                hashedData[str(eachRow[0])] = str(eachRow[1])
                                                return hashedData
#                                              return StaticDevices
                                except Exception as e:
                                                return {'error': str(e)}


#####NoCcmDevices#####
#Lists devices that have reported audit data or contacted sophos but havent contacted SCCM for 3 days split into mobile and static devices
@api.route("/NoCcmDevices")
class NoCcmDevices(Resource):
                def post(self):
                                try:
                                                sql = "SELECT SUBSTRING_INDEX(Hostname,'.',1),LastReported,SCCM,SCCMupdated,(DATEDIFF(GREATEST(COALESCE(LastReported,0),COALESCE(Sophos,0)),SCCM)),Sophos FROM AuditLastReported WHERE GREATEST(COALESCE(LastReported,0),COALESCE(Sophos,0)) - INTERVAL 2 DAY > SCCM AND SCCM IS NOT null AND ((Hostname LIKE '%DESKTOP%') OR (Hostname LIKE '%VDI%')) AND (SCCMupdated = (SELECT MAX(SCCMupdated) FROM AuditLastReported WHERE Hostname LIKE '%DESKTOP%'))"
                                                cursor.execute(sql)
                                                NoCcmList = cursor.fetchall()
                                                hashedData = {}
                                                for eachRow in NoCcmList:
                                                                hashedData[str(eachRow[0])] = str(eachRow[1])
                                                return hashedData
                                except Exception as e:
                                                return {'error': str(e)}


#####TargetPatchLevel#####
#Sets a patch level for a speicifed build version in tblPatchingTargets
target_patch_args = reqparse.RequestParser()
target_patch_args.add_argument('BuildVersion', type=str, help='Build version')
target_patch_args.add_argument('TargetPatchLevel', type=str, help='Target patch level for specified build version')

@api.route("/TargetPatchLevel")
class TargetPatchLevel(Resource):
                @api.doc(parser=target_patch_args)
                def post(self):
                                try:
                                                args = target_patch_args.parse_args()
                                                BuildVersion = args['BuildVersion']
                                                TargetPatchLevel = args['TargetPatchLevel']
                                                if (BuildVersion):
                                                                if (TargetPatchLevel):
                                                                                sql = "INSERT INTO tblPatchingTargets(BuildVersion,TargetPatchLevel) VALUES('" + BuildVersion + "', '" + TargetPatchLevel + "') ON DUPLICATE KEY UPDATE BuildVersion='" + BuildVersion + "', TargetPatchLevel='" + TargetPatchLevel + "'"
                                                                                cursor.execute(sql)
                                                sql = "SELECT * FROM tblPatchingTargets"
                                                cursor.execute(sql)
                                                data = cursor.fetchall()
                                                return data
                                except Exception as e:
                                                return {'error': str(e)}


#####UpdatePatchLevel#####
#Records a patchlevel for a specified device
update_patch_args = reqparse.RequestParser()
update_patch_args.add_argument('hostname', type=str, help='Hostname of machine to update')
update_patch_args.add_argument('buildversion', type=str, help='Build version: major.minor.build.revision')

@api.route("/UpdatePatchLevel")
class UpdatePatchLevel(Resource):
                @api.doc(parser=update_patch_args)
                def post(self):
                                try:
                                                args = update_patch_args.parse_args()
                                                hostname = args['hostname']
                                                buildarg = args['buildversion']
                                                buildversion = buildarg.split(".")
                                                major = buildversion[0]
                                                minor = buildversion[1]
                                                build = buildversion[2]
                                                revision = buildversion[3]
                                                sql = "INSERT INTO AuditLastReported(Hostname,Major,Minor,Build,Revision) VALUES('" + hostname + "', " + major + ", " + minor + ", " + build + ", " + revision + ") ON DUPLICATE KEY UPDATE Hostname='" + hostname + "', Major=" + major + ", Minor=" + minor + ", Build=" + build + ", Revision=" + revision
                                                cursor.execute(sql)
                                                sql = "SELECT Hostname,Major,Minor,Build,Revision FROM AuditLastReported WHERE Hostname='" + hostname + "'"
                                                cursor.execute(sql)
                                                data = cursor.fetchall()
                                                conn.commit()
                                                return {'hostname': str(data[0][0]), 'BuildVersion': str(data[0][1]) + "." + str(data[0][2]) + "." + str(data[0][3]) + "." + str(data[0][4])}
                                except Exception as e:
                                                return {'error': str(e)}


#####UpdateSCCM#####
#Updates a row to record when a specified device last reported to SCCM
update_sccm_args = reqparse.RequestParser()
update_sccm_args.add_argument('hostname', type=str, help='Hostname of machine to update')
update_sccm_args.add_argument('updateTimestamp', type=str, help='Last update date (yyyymmdd)')

@api.route("/UpdateSCCM")
class UpdateSCCM(Resource):
                @api.doc(parser=update_sccm_args)
                def post(self):
                                try:
                                                lastUpdated = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
                                                args = update_sccm_args.parse_args()
                                                hostname = args['hostname']
                                                updateTimestamp = args['updateTimestamp']
                                                sql = "INSERT INTO AuditLastReported(Hostname,SCCM,SCCMupdated) VALUES('" + hostname + "', '" + updateTimestamp + "', '" + lastUpdated + "') ON DUPLICATE KEY UPDATE Hostname='" + hostname + "', SCCM='" + updateTimestamp + "', SCCMupdated='" + lastUpdated + "'"
                                                cursor.execute(sql)
                                                sql = "SELECT * FROM AuditLastReported WHERE Hostname='" + hostname + "'"
                                                cursor.execute(sql)
                                                data = cursor.fetchall()
                                                conn.commit()
                                                return {'hostname': str(data[0][0]), 'auditTimestamp': str(data[0][1]), 'updateTimestamp': str(data[0][2])}
                                except Exception as e:
                                                return {'error': str(e)}


#####UpdateSophos#####
#Updates a row to record when a specified device last reported to Sophos
sophos_args = reqparse.RequestParser()
sophos_args.add_argument('hostname', type=str, help='Hostname of machine to update')
sophos_args.add_argument('updateTimestamp', type=str, help='Last update date (yyyymmdd)')

@api.route("/UpdateSophos")
class UpdateSophos(Resource):
                @api.doc(parser=sophos_args)
                def post(self):
                                try:
                                                lastUpdated = str(datetime.today().strftime("%Y%m%d"))
                                                args = sophos_args.parse_args()
                                                hostname = args['hostname']
                                                updateTimestamp = args['updateTimestamp']
                                                sql = "INSERT INTO AuditLastReported(Hostname,Sophos,SophosImported) VALUES('" + hostname + "', '" + updateTimestamp + "', '" + lastUpdated + "') ON DUPLICATE KEY UPDATE Hostname='" + hostname + "', Sophos='" + updateTimestamp + "', SophosImported='" + lastUpdated + "'"
                                                cursor.execute(sql)
                                                sql = "SELECT Hostname,Sophos,SophosImported FROM AuditLastReported WHERE Hostname='" + hostname + "'"
                                                cursor.execute(sql)
                                                data = cursor.fetchall()
                                                conn.commit()
                                                return {'hostname': str(data[0][0]), 'auditTimestamp': str(data[0][1]), 'updateTimestamp': str(data[0][2])}
                                except Exception as e:
                                                return {'error': str(e)}


#Execute the API on specified host and port
if __name__=="__main__":
    app.run(host="0.0.0.0",port=8001)
