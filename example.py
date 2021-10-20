import mysql.connector
from mysql.connector import errorcode


dbconfig = {'user': 'root',
            'password': 'root',
            'host': '127.0.0.1',
            'database': 'taxdata',
            'raise_on_warnings': True}

try:
    cnx = mysql.connector.connect(**dbconfig)
    # cnx = mysql.connector.connect(user='root', password='root',
    #                               host='127.0.0.1',database='testDB')
    cursor = cnx.cursor()
    cus_id = cursor.lastrowid
    print(cus_id)
    print('\n')

    # data format to be entered
    add_client = ("INSERT INTO taxdata.clients (clientid, firstname, lastname, pan) "
                  "VALUES (%(client_id)s, %(first_name)s, %(last_name)s, %(pan)s)")
    # add_address = ("INSERT INTO taxdata.address"
    #                "(clientid, streetnumber, housenum, streetname, locality, city, state, pin) "
    #                "VALUES (%(client_id)d, %(street_num)s, %(house_num)s, %(street_name)s, %(locale)s, %(city)s,"
    #                "%(state)s, %(pin)s)")
    # add_identity = ("INSERT INTO taxdata.identity "
    #                 "(pan, clientid, portalpass)"
    #                 "VALUES (%(pan)s, %(client_id)s, %(portal_pass)s)")

    data_client = {'client_id': int(20003), 'first_name': 'Jane', 'last_name': 'Doe', 'pan': 'AXYD1234ST'}

    # Insert new client
    cursor.execute(add_client, data_client)
    client_id = cursor.lastrowid

    print(client_id)
    print('\n')

    # making sure data is commited to db
    cnx.commit()

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
# from mysql.connector import (connection)
# cnx = connection.MySQLConnection(user='root', password='root',
#                                  host='127.0.0.1', database='testDB')
# cnx.close()



