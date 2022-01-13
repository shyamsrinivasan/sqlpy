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
    add_client = ("INSERT INTO {}.clients "
                  "(clientid, firstname, lastname, pan) "
                  "VALUES (%(client_id)s, %(first_name)s, %(last_name)s, %(pan)s)".format(dbconfig['database']))
    add_address = ("INSERT INTO {}.address "
                   "(clientid, streetnumber, streetname, housenum, locality, city, state, pin) "
                   "VALUES (%(client_id)s, %(street_num)s, %(street_name)s, %(house_num)s, %(locality)s, %(city)s, "
                   "%(state)s, %(pin)s)".format(dbconfig['database']))
    add_identity = ("INSERT INTO {}.identity "
                    "(clientid, pan, portalpass) "
                    "VALUES (%(client_id)s, %(pan)s, %(portalpass)s)".format(dbconfig['database']))

    client_data = {'client_id': 20006, 'first_name': 'Shikamaru', 'last_name': 'Nara', 'pan': 'SDRF2546RT',
                   'street_num': '1', 'street_name': 'nowhere st', 'house_num': '', 'locality': '', 'city': 'Everywhere',
                   'state': 'This', 'pin': 600001, 'portalpass': 'xdst45Ds3rf98S'}
    add2db(dbconfig, add_client, client_data)
    add2db(dbconfig, add_identity, client_data)
    add2db(dbconfig, add_address, client_data)

    # query to check addition to db
    querydb(dbconfig, query, printflag=True)



    # add_address = "INSERT INTO address"

    # display all databases in the current SQL server
    # showdb_query = "SHOW DATABASES"
    # cursor.execute(showdb_query)
    # for db in cursor:
    #     print(db)







