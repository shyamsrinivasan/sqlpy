import mysql.connector
from mysql.connector import errorcode


def querydb(dbconfig=None, query='', query_args=None, printflag=False):
    """connect to mysql db using connector and query, add to or
    update db using relevant queries passed as input"""

    flag = False
    if dbconfig is None:
        print('Empty database configuration information')
        return flag
    else:
        try:
            cnx = mysql.connector.connect(**dbconfig)
            cursor = cnx.cursor()
            if query_args is None:
                cursor.execute(query)
            else:
                cursor.execute(query, query_args)  # execute given query in mysql object

            if printflag:
                # print statement only good for taxdb.clients
                for (first_name, last_name, client_id) in cursor:
                    print("{} {} is a client with ID: {}".format(first_name, last_name, client_id))

            cnx.commit()
            flag = True

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            cnx.rollback()
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()
    return flag


def getinfo(dbconfig: dict, query, id_only=False, query_args=None, address=False, identity=False):
    """get entries from db using given query. Fetch all relevant details from all tables in db"""

    client = None
    try:
        cnx = mysql.connector.connect(**dbconfig)
        cursor = cnx.cursor(dictionary=True)
        if query_args is None:
            cursor.execute(query)
        else:
            cursor.execute(query, query_args)  # execute given query in mysql object
        fname, lname, cid, pan = [], [], [], []
        snum, sname, housenum, locale, city, state, pin = [], [], [], [], [], [], []
        portalpass = []
        for row in cursor:
            # client info
            cid.append(row['clientid'])
            if not id_only:
                fname.append(row['firstname'])
                lname.append(row['lastname'])
                pan.append(row['pan'])
            # address info
            if address:
                sname.append(row['streetname'])
                snum.append(row['streetnumber'])
                housenum.append(row['housenum'])
                locale.append(row['locality'])
                city.append(row['city'])
                state.append(row['state'])
                pin.append(row['pin'])
            # identity
            if identity:
                portalpass.append(row['portalpass'])
        client = {'firstname': fname, 'lastname': lname, 'clientid': cid, 'pan': pan, 'streetnumber': snum,
                  'streetname': sname, 'housenum': housenum, 'locality': locale, 'city': city, 'state': state,
                  'pin': pin, 'portalpass': portalpass}
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        cnx.rollback()
    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()
    return client


def check_db(dbconfig: dict, info: dict, qtype=-1, get_address=False, get_password=False):
    """check if given client part of DB based on given info (name/pan/client id)
    and return all details of said client"""

    if get_address and get_password:
        if qtype == 1:       # get info with clientid
            query = ("SELECT * FROM clients LEFT JOIN (address, identity)"
                     "ON (clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
                     "clients.clientid = %(clientid)s)")
        elif qtype == 2:     # get info using name
            query = ("SELECT * FROM clients LEFT JOIN (address, identity)"
                     "ON (clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
                     "(clients.firstname = %(firstname)s OR clients.lastname = %(lastname)s)")
        elif qtype == 3:     # get info using pan
            query = ("SELECT * FROM clients LEFT JOIN (address, identity)"
                     "ON (clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
                     "clients.pan = %(pan)s")
        else:   # get info using clientid, name or pan
            query = ("SELECT * FROM clients LEFT JOIN (address, identity)"
                     "ON (clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
                     "(clients.clientid = %(clientid)s OR clients.firstname = %(firstname)s OR "
                     "clients.lastname = %(lastname)s OR clients.pan = %(pan)s)")
        dbinfo = getinfo(dbconfig, query, query_args=info, address=True, identity=True)
    elif get_address and not get_password:
        if qtype == 1:  # get info with clientid
            query = ("SELECT * FROM clients LEFT JOIN address "
                     "ON (clients.clientid=address.clientid AND clients.clientid = %(clientid)s) "
                     "WHERE address.streetname is NOT NULL OR address.streetnumber is NOT NULL OR "
                     "address.housenum is NOT NULL OR address.locality is NOT NULL OR address.city is NOT NULL OR "
                     "address.state is NOT NULL")
        elif qtype == 2:  # get info using name
            query = ("SELECT * FROM clients LEFT JOIN address "
                     "ON (clients.clientid=address.clientid AND (clients.firstname = %(firstname)s OR "
                     "clients.lastname = %(lastname)s) WHERE address.streetname is NOT NULL OR "
                     "address.streetnumber is NOT NULL OR address.housenum is NOT NULL OR address.locality is NOT NULL "
                     "OR address.city is NOT NULL OR address.state is NOT NULL")
        elif qtype == 3:  # get info using pan
            query = ("SELECT * FROM clients LEFT JOIN address "
                     "ON (clients.clientid=address.clientid AND clients.pan = %(pan)s WHERE "
                     "address.streetname is NOT NULL OR address.streetnumber is NOT NULL OR "
                     "address.housenum is NOT NULL OR address.locality is NOT NULL OR address.city is NOT NULL OR "
                     "address.state is NOT NULL")
        else:  # get info using clientid, name or pan
            query = ("SELECT * FROM clients LEFT JOIN address "
                     "ON (clients.clientid=address.clientid AND "
                     "(clients.clientid = %(clientid)s OR clients.firstname = %(firstname)s OR "
                     "clients.lastname = %(lastname)s OR clients.pan = %(pan)s) WHERE address.streetname is NOT NULL "
                     "OR address.streetnumber is NOT NULL OR address.housenum is NOT NULL OR "
                     "address.locality is NOT NULL OR address.city is NOT NULL OR address.state is NOT NULL")
        dbinfo = getinfo(dbconfig, query, query_args=info, address=True)
        # remove all row entries corresponding to a None entry (SQL output is NULL for respective row)
        # remove_row()
    else:
        if qtype == 1:   # check using client ID
            query = ("SELECT firstname, lastname, clientid, pan FROM taxdata.clients "
                     "WHERE clientid = %(clientid)s")
        elif qtype == 2:     # get info using name
            query = ("SELECT firstname, lastname, clientid, pan FROM taxdata.clients "
                     "WHERE firstname = %(firstname)s OR lastname = %(lastname)s")
        elif qtype == 3:      # get info using pan
            query = ("SELECT firstname, lastname, clientid, pan FROM taxdata.clients "
                     "WHERE pan = %(pan)s")
        else:   # check using all of the above
            query = ("SELECT firstname, lastname, clientid, pan FROM taxdata.clients "
                     "WHERE firstname = %(firstname)s OR lastname = %(lastname)s OR "
                     "pan = %(pan)s OR clientid = %(clientid)s")
        dbinfo = getinfo(dbconfig, query, query_args=info)
    return dbinfo


def updatedb(dbconfig: dict, up_fields: list, query: dict, query_args: dict):
    """update client entries in DB using buffered cursor"""

    flag = False
    try:
        cnx = mysql.connector.connect(**dbconfig)
        cursor = cnx.cursor(buffered=True)
        if all(up_fields):
            cursor.execute(query['all'], query_args)    # execute given query in mysql object
            cnx.commit()    # commit changes to db
        else:
            if up_fields[0]:
                cursor.execute(query['streetnumber'], query_args)
                cnx.commit()
            if up_fields[1]:
                cursor.execute(query['streetname'], query_args)
                cnx.commit()
            if up_fields[2]:
                cursor.execute(query['housenum'], query_args)
                cnx.commit()
            if up_fields[3]:
                cursor.execute(query['locality'], query_args)
                cnx.commit()
            if up_fields[4]:
                cursor.execute(query['city'], query_args)
                cnx.commit()
            if up_fields[5]:
                cursor.execute(query['state'], query_args)
                cnx.commit()
            if up_fields[6]:
                cursor.execute(query['pin'], query_args)
                cnx.commit()
        cnx.close()
        flag = True
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        cnx.rollback()
    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()
    return flag
