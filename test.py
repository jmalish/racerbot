from mysql.connector import connection as my_sql
import json

with open('pysecrets.json') as jsonfile:  # get contents of secrets file (contains api keys)
    secrets = json.load(jsonfile)

sql_user = secrets["mySQLuser"]  # user for mySQL
sql_pass = secrets["mySQLpass"]


try:
    sql_connection = my_sql.MySQLConnection(user=sql_user, password=sql_pass,  # open connection to mySQL
                                            host="jordanmalish.com", database="racerbot")

    sql_cursor = sql_connection.cursor()  # cursor for mySQL

    sql_query = "SELECT * FROM quotes"  # query to be sent to sql
    sql_cursor.execute(sql_query)  # send query to sql

    for quote in sql_cursor:  # for each response
        quote_id = quote[0]
        quote_user = quote[1]
        quote_text = quote[2]
        print "#%s - %s: %s" % (quote_id, quote_user, quote_text)

    sql_connection.close()  # close connection to mySQL when done
except Exception, e:
    print e
