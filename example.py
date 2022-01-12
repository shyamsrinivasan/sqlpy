from query import querydb, add2db


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
    # query = "SELECT firstname, lastname FROM taxdata.clients WHERE clientid=%(client_id)s;"
    # detail = {'client_id': 20002}
    querydb(dbconfig, query, printflag=True)

    # step 2 - connect to sql db/add values to db
    # insert data into existing db table
    add_client = ("INSERT INTO taxdata.clients "
                  "(clientid, firstname, lastname, pan) "
                  "VALUES (%(client_id)s, %(first_name)s, %(last_name)s, %(pan)s)")
    client_data = {'client_id': 20005, 'first_name': 'Neji', 'last_name': 'Hyuga', 'pan': 'BXTC5489SD'}
    add2db(dbconfig, add_client, client_data)

    # query to check addition to db
    querydb(dbconfig, query, printflag=True)


    # add_identity = "INSERT INTO identity"
    # add_address = "INSERT INTO address"

    # display all databases in the current SQL server
    # showdb_query = "SHOW DATABASES"
    # cursor.execute(showdb_query)
    # for db in cursor:
    #     print(db)







