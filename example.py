import mysql.connector
from mysql.connector import errorcode


dbconfig = {'user': 'root',
            'password': 'root',
            'host': '127.0.0.1',
            'database': 'taxdata',
            'raise_on_warnings': True}

try:
    cnx = mysql.connector.connect(**dbconfig)
    cursor = cnx.cursor()

    query = "SELECT firstname, lastname FROM taxdata.clients WHERE clientid=%(client_id)s;"

    detail = {'client_id': 20002}
    # Search SQL db
    cursor.execute(query, detail)

    for (first_name, last_name) in cursor:
        print("{} {} is a client".format(first_name, last_name))

    cursor.close()
    cnx.close()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Username or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cnx.close()




