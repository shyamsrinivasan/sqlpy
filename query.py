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
            cnx.commit()
            flag = True
            if printflag:
                # print statement only good for taxdb.clients
                for (first_name, last_name, client_id) in cursor:
                    print("{} {} is a client with ID: {}".format(first_name, last_name, client_id))

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


def getinfo(dbconfig: dict, info: dict, query, address=False, identity=False):
    """get entries from db using given query. Fetch all relevant details from all tables in db"""

    # check if name/pan present in any one of three tables
    # query = ("SELECT firstname, lastname, clientid, pan FROM taxdata.clients "
    #          "WHERE firstname = %(firstname)s OR lastname = %(lastname)s OR pan = %(pan)s")
    # query = ("SELECT firstname, lastname, clientid FROM {}.clients".format(dbconfig["database"]))
    # query = ("SELECT * FROM clients LEFT JOIN (address, identity) "
    #          "ON (clients.clientid=address.clientid AND clients.clientid=identity.clientid AND clients.clientid=20001)")

    client = None
    try:
        cnx = mysql.connector.connect(**dbconfig)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, info)  # execute given query in mysql object
        fname, lname, cid, pan = [], [], [], []
        snum, sname, housenum, locale, city, state, pin = [], [], [], [], [], [], []
        portalpass = []
        for row in cursor:
            # client info
            cid.append(row['clientid'])
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


def check_db(dbconfig: dict, info: dict, type=-1, get_address=False, get_password=False):
    """check if given client part of DB based on given info (name/pan/client id)
    and return all details of said client"""

    # ("SELECT * FROM clients LEFT JOIN (address, identity) "
    #  #          "ON (clients.clientid=address.clientid AND clients.clientid=identity.clientid AND clients.clientid=20001)")

    if get_address and get_password:
        if type == 1:       # get info with clientid
            query = ("SELECT * FROM clients LEFT JOIN (address, identity)"
                     "ON (clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
                     "clients.clientid = %(clientid)s)")
        elif type == 2:     # get info using name
            query = ("SELECT * FROM clients LEFT JOIN (address, identity)"
                     "ON (clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
                     "(clients.firstname = %(firstname)s OR clients.lastname = %(lastname)s)")
        elif type == 3:     # get info using pan
            query = ("SELECT * FROM clients LEFT JOIN (address, identity)"
                     "ON (clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
                     "clients.pan = %(pan)s")
        else:   # get info using clientid, name or pan
            query = ("SELECT * FROM clients LEFT JOIN (address, identity)"
                     "ON (clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
                     "(clients.clientid = %(clientid)s OR clients.firstname = %(firstname)s OR "
                     "clients.lastname = %(lastname)s OR clients.pan = %(pan)s)")
        dbinfo = getinfo(dbconfig, info, query, address=True, identity=True)
    elif get_address and not get_password:
        if type == 1:  # get info with clientid
            query = ("SELECT * FROM clients LEFT JOIN address"
                     "ON (clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
                     "clients.clientid = %(clientid)s)")
        elif type == 2:  # get info using name
            query = ("SELECT * FROM clients LEFT JOIN address"
                     "ON (clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
                     "(clients.firstname = %(firstname)s OR clients.lastname = %(lastname)s)")
        elif type == 3:  # get info using pan
            query = ("SELECT * FROM clients LEFT JOIN address"
                     "ON (clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
                     "clients.pan = %(pan)s")
        else:  # get info using clientid, name or pan
            query = ("SELECT * FROM clients LEFT JOIN address"
                     "ON (clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
                     "(clients.clientid = %(clientid)s OR clients.firstname = %(firstname)s OR "
                     "clients.lastname = %(lastname)s OR clients.pan = %(pan)s)")
        dbinfo = getinfo(dbconfig, info, query, address=True)
    else:
        if type == 1:   # check using client ID
            query = ("SELECT firstname, lastname, clientid, pan FROM taxdata.clients "
                     "WHERE clientid = %(clientid)s")
        elif type == 2:     # get info using name
            query = ("SELECT firstname, lastname, clientid, pan FROM taxdata.clients "
                     "WHERE firstname = %(firstname)s OR lastname = %(lastname)s")
        elif type == 3:      # get info using pan
            query = ("SELECT firstname, lastname, clientid, pan FROM taxdata.clients "
                     "WHERE pan = %(pan)s")
        else:   # check using all of the above
            query = ("SELECT firstname, lastname, clientid, pan FROM taxdata.clients "
                     "WHERE firstname = %(firstname)s OR lastname = %(lastname)s OR "
                     "pan = %(pan)s OR clientid = %(clientid)s")
        dbinfo = getinfo(dbconfig, info, query)
    return dbinfo



    # steps to update client info
    # 1. check if info (identity) in db is same as provided info
    # 2. if TRUE - do not update
    # 3. else (FALSE) - update db entries

    flag = False
    try:
        cnx = mysql.connector.connect(**dbconfig)
        cursor = cnx.cursor()
        cursor.execute(query, data)  # execute given query in mysql object
        cnx.commit()  # commit changes to db
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
    return


# def query_address(dbconfig: dict, info: dict):
#     """check if client is already present in db and get address, if present"""
#
#     # check if name/pan present in any one of three tables
#     query = ("SELECT clientid, streetnumber, streetname, housenum, locality, city, state, pin FROM taxdata.address"
#              "WHERE clientid = %(clientid)s")
#     address = None
#     try:
#         cnx = mysql.connector.connect(**dbconfig)
#         cursor = cnx.cursor(dictionary=True)
#         cursor.execute(query, info)  # execute given query in mysql object
#         cid, snum, sname, housenum, locale, city, state, pin = [], [], [], [], [], [], [], []
#         for row in cursor:
#             sname.append(row['streetname'])
#             snum.append(row['streetnumber'])
#             cid.append(row['clientid'])
#             housenum.append(row['housenum'])
#             locale.append(row['locality'])
#             city.append(row['city'])
#             state.append(row['state'])
#             pin.append(row['pin'])
#         address = {'clientid': cid, 'streetnumber': snum, 'streetname': sname, 'housenum': housenum, 'locality': locale,
#                    'city': city, 'state': state, 'pin': pin}
#     except mysql.connector.Error as err:
#         if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#             print("Username or password")
#         elif err.errno == errorcode.ER_BAD_DB_ERROR:
#             print("Database does not exist")
#         else:
#             print(err)
#         cnx.rollback()
#     finally:
#         if cnx.is_connected():
#             cursor.close()
#             cnx.close()
#     return address


# def query_identity(dbconfig: dict, info: dict):
#     """Query identity table for all field/column information"""
#
#     # check if name/pan present in any one of three tables
#     query = ("SELECT clientid, streetnumber, streetname, housenum, locality, city, state, pin FROM taxdata.address"
#              "WHERE clientid = %(clientid)s")
#     identity = None
#     try:
#         cnx = mysql.connector.connect(**dbconfig)
#         cursor = cnx.cursor(dictionary=True)
#         cursor.execute(query, info)  # execute given query in mysql object
#         cid, pan, portalpass = [], [], []
#         for row in cursor:
#             cid.append(row['clientid'])
#             pan.append(row['pan'])
#             portalpass.append(row['portalpass'])
#         identity = {'clientid': cid, 'pan': pan, 'portalpass': portalpass}
#     except mysql.connector.Error as err:
#         if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#             print("Username or password")
#         elif err.errno == errorcode.ER_BAD_DB_ERROR:
#             print("Database does not exist")
#         else:
#             print(err)
#         cnx.rollback()
#     finally:
#         if cnx.is_connected():
#             cursor.close()
#             cnx.close()
#     return identity


# def get_client_id(dbconfig: dict, info: dict):
#     """Get client ID for all given first names or last names or both"""
#
#     client_id = []
#     for i_client in info:
#         cid = query_client(dbconfig, i_client)
#         client_id.append(cid[0])
#
#     return client_id


def check_update(dbconfig: dict, info: dict):
    """check if current entries for existing clients are same as one provided. If not, update entry.
    Update only entries that are different"""

    # check client info using
    query = ("SELECT firstname, lastname FROM {}.clients")
    # check address info
    # check identity info

    return


def update_client(dbconfig: dict, data: dict):
    update_cl = ("UPDATE tablename SET colname = colvalue")
    # update_db(dbconfig, update_cl, data)
    return


def update_address(dbconfig: dict, data: dict):
    update_add = ("UPDATE")
    # query = ("UPDATE tablename SET colname = colvalue")
    # update_db(dbconfig, update_add, data)
    return


def update_identity(dbconfig: dict, data: dict):
    update_id = ("UPDATE")
    # update_db(dbconfig, update_id, data)
    return


def updatesingleentry(dbconfig: dict, data: dict, entry_type=-1):
    """update a single/single type of entry in db
    entry_type == 1 for update client only
    entry_type == 2 for update address only
    entry_type == 3 for update identity (password) only"""

    if entry_type == 1:  # add client only
        update_client(dbconfig, data)
    elif entry_type == 2:  # add address only
        update_address(dbconfig, data)
    elif entry_type == 3:  # add identity only
        update_identity(dbconfig, data)
    else:   # add all client, address and identity
        update_client(dbconfig, data)
        update_address(dbconfig, data)
        update_identity(dbconfig, data)
    return



