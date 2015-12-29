import mysql.connector as mysql
import json
import time
import random

# API Key variables
with open('pysecrets.json') as jsonfile:  # get contents of secrets file (contains api keys)
    secrets = json.load(jsonfile)

sql_user = secrets["mySQLuser"]
sql_pass = secrets["mySQLpass"]


def add_last_message(username, message):
    try:
        # connect to db
        sql_db = mysql.connect(host="jordanmalish.com", user=sql_user, passwd=sql_pass, db="racerbot")

        sql_cursor = sql_db.cursor()  # create cursor, this reads and writes to the db

        # make sure we have this user in db
        sql_cursor.execute("SELECT 1 FROM last_messages WHERE user=%s", (username,))
        if len(sql_cursor.fetchall()) > 0:  # if the user does exist, update the last message
            sql_cursor.execute('UPDATE last_messages SET message_text=%s, time=NOW() WHERE user=%s',
                               (message, username))
        else:  # if not, create a new row with the username and last message
            sql_cursor.execute('INSERT INTO last_messages (user, message_text, time) VALUES (%s, %s, NOW())',
                               (username, message))

        sql_db.commit()  # commit the data to the database
        sql_cursor.close()
        sql_db.close()  # close database connection
    except Exception, e:
        print "Something went wrong in add_last_message(%s, %s)" % (username, message)
        print e


# gets number of quotes in system
def get_quotes():
    try:
        sql_db = mysql.connect(host="jordanmalish.com", user=sql_user, passwd=sql_pass, db="racerbot")
        sql_cursor = sql_db.cursor()

        sql_cursor.execute("SELECT * FROM quotes")
        quotes = sql_cursor.fetchall()

        sql_cursor.close()
        sql_db.close()
        return quotes
    except Exception, e:
        print "Something went wrong in get_quotes()"
        print e


# grab last message from given user
def grab(username):
    try:
        sql_db = mysql.connect(host="jordanmalish.com", user=sql_user, passwd=sql_pass, db="racerbot")
        sql_cursor = sql_db.cursor()

        # make sure the user actually said something
        sql_cursor.execute("SELECT * FROM last_messages where user=%s", (username,))
        message = sql_cursor.fetchall()

        if len(message) > 0:  # if the user does exist, get message
            m_date = message[0][0]
            m_user = message[0][1]
            m_quote = message[0][2]
            # insert quote
            sql_cursor.execute('INSERT INTO quotes (user, quote_text, time) VALUES (%s, %s, %s)',
                               (m_user, m_quote, m_date))

            sql_db.commit()
            print "Quote grabbed"

            sql_cursor.close()
            sql_db.close()
            return True
        else:  # if not, create a new row with the username and last message
            sql_cursor.close()
            sql_db.close()
            return False
    except Exception, e:
        print "Something went wrong in grab(%s)" % username
        print e
