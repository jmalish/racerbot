import mysql.connector as mysql
import json
from datetime import datetime

# with open('pysecrets.json') as jsonfile:  # get contents of secrets file (contains api keys)
#     secrets = json.load(jsonfile)
#
# sql_user = secrets["mySQLuser"]
# sql_pass = secrets["mySQLpass"]
#
# username = "racer0940"
#
# sql_db = mysql.connect(host="jordanmalish.com", user=sql_user, passwd=sql_pass, db="racerbot")
# sql_cursor = sql_db.cursor()
#
# # make sure the user actually said something
# sql_cursor.execute("SELECT * FROM last_messages where user=%s", (username,))
#
# message = sql_cursor.fetchone()
#
# sql_cursor.close()
# sql_db.close()

import irc_quotes


message = ".lastseen  racer0940"

user = message.split(".lastseen ")[1].strip()

print user

