# import mysql.connector as mysql
# import json
#
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
# message = sql_cursor.fetchall()[0][2]
# sql_cursor.close()
# sql_db.close()

import irc_quotes

message = ".quote 2"

quotes = irc_quotes.get_quotes()  # get all quotes from the table
if message.split(".quote")[1].strip():
    quote_number = int(message.split(".quote")[1].strip()) - 1
    quote_user = quotes[quote_number][1]  # get each part of quote
    quote_message = quotes[quote_number][2]
    print("#%s - %s: %s" % (quote_number + 1, quote_user, quote_message))

