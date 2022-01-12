import mysql.connector
from mysql.connector import errorcode
from query import querydb


if __name__ == '__main__':
    """script to test mySQL python connector"""
    # step 1 - connect to sql db/query db for values
    dbconfig = {'user': 'root',
                'password': 'root',
                'host': '127.0.0.1',
                'database': 'taxdata',
                'raise_on_warnings': True}

    # query = "SELECT firstname, lastname FROM taxdata.clients WHERE clientid=%(client_id)s;"
    # detail = {'client_id': 20002}
    query = "SELECT firstname, lastname, clientid FROM clients;"
    querydb(dbconfig, query, printflag=True)

    # display all databases in the current SQL server
    # showdb_query = "SHOW DATABASES"

    # step 2 - connect to sql db/add values to db

    try:
        cnx = mysql.connector.connect(**dbconfig)
        cursor = cnx.cursor()

        # insert data into existing db table
        # add_client = ("INSERT INTO clients "
        #               "(clientid, firstname, lastname, pan) "
        #               "VALUES (%(client_id)s, %(first_name)s, %(last_name)s, %(pan)s)")
        # # add_identity = "INSERT INTO identity"
        # # add_address = "INSERT INTO address"
        # client_data = {'client_id': 20004, 'first_name': 'Asuma', 'last_name': 'Sarutobi', 'pan': 'SATC1248XY'}

        # mysql db query
        # query = "SELECT firstname, lastname FROM taxdata.clients WHERE clientid=%(client_id)s;"
        # detail = {'client_id': 20002}
        query = "SELECT firstname, lastname, clientid FROM clients;"

        # cursor.execute(add_client, client_data)
        cursor.execute(query)

        # show all db in SQL server
        # cursor.execute(showdb_query)
        # for db in cursor:
        #     print(db)

        for (first_name, last_name, client_id) in cursor:
            print("{} {} is a client with ID: {}".format(first_name, last_name, client_id))

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




