import mysql.connector
from mysql.connector import errorcode
import pandas as pd


def querydb(dbconfig=None, query='', query_args=None, printflag=False):
    """connect to mysql db using connector"""

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
            # else:  # pass cursor output

            flag = True

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()

    return flag


def add2db(dbconfig, add_query, add_data):
    """add data to tables in existing db"""

    flag = False
    try:
        cnx = mysql.connector.connect(**dbconfig)
        cursor = cnx.cursor()
        cursor.execute(add_query, add_data)  # execute given query in mysql object
        cnx.commit()    # commit changes to db
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


def check_client(dbconfig: dict, info: dict):
    """check if client is already present in db"""

    # check if name/pan present in any one of three tables
    query = ("SELECT firstname, lastname, clientid FROM taxdata.clients "
             "WHERE firstname = %(firstname)s OR lastname = %(lastname)s OR pan = %(pan)s")
    # query = ("SELECT firstname, lastname, clientid FROM {}.clients".format(dbconfig["database"]))

    present = False
    try:
        cnx = mysql.connector.connect(**dbconfig)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, info)  # execute given query in mysql object
        fname, lname, cid = [], [], []
        for row in cursor:
            fname.append(row['firstname'])
            lname.append(row['lastname'])
            cid.append(row['clientid'])
        if fname or lname or cid:
            # print("Client {} {} with ID {} is present in DB".format(fname, lname, cid))
            present = True
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
    return present, cid


def addclient(dbconfig: dict, details: dict):
    """add client name details to db"""

    add_client = ("INSERT INTO {}.clients "
                  "(clientid, firstname, lastname, pan) "
                  "VALUES (%(client_id)s, %(firstname)s, %(lastname)s, %(pan)s)".format(dbconfig['database']))
    flag = add2db(dbconfig, add_client, details)
    return flag


def addaddress(dbconfig: dict, details: dict):
    """add client address details to db"""

    add_address = ("INSERT INTO {}.address "
                   "(clientid, streetnumber, streetname, housenum, locality, city, state, pin) "
                   "VALUES (%(client_id)s, %(street_num)s, %(street_name)s, %(house_num)s, %(locality)s, %(city)s, "
                   "%(state)s, %(pin)s)".format(dbconfig['database']))
    flag = add2db(dbconfig, add_address, details)
    return flag


def addidentity(dbconfig: dict, details: dict):
    """add client identity details to db"""

    add_identity = ("INSERT INTO {}.identity "
                    "(clientid, pan, portalpass) "
                    "VALUES (%(client_id)s, %(pan)s, %(portalpass)s)".format(dbconfig['database']))
    flag = add2db(dbconfig, add_identity, details)
    return flag


def assignid(dbconfig: dict, data: object) -> object:
    """assign client ids to new clients from client info file"""

    # search db for latest clientid
    query = ("SELECT clientid FROM {}.clients".format(dbconfig['database']))
    try:
        cnx = mysql.connector.connect(**dbconfig)
        cursor = cnx.cursor()
        cursor.execute(query)  # execute given query in mysql object
        flag = True
        all_clientid = [clientid[0] for clientid in cursor]
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        all_clientid = None
    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()

    # get last client id - client id increases sequentially
    if all_clientid is not None:
        large_id = all_clientid[0]
        for id in all_clientid:
            if id > large_id:
                large_id = id
        # add client ids to new clients
        nrows = data.shape[0]
        large_id += 1
        new_client_ids = [large_id + irow for irow in range(0, nrows)]
        data = data.assign(client_id=pd.Series(new_client_ids))
    else:
        print('Could not access database to get existing client ID: Assign client ID manually \n')

    return data


def loadclientinfo(data: object, dbconfig=None):
    """load client info from dataframe to db"""

    # assign client id to new clients
    data = assignid(dbconfig, data)

    client_list = data.to_dict('records')
    for i_client in client_list:
        # check if new client in db (same name/pan)
        present, cid = check_client(dbconfig, i_client)
        if present:     # if present, only update existing entry (address) or return error
            print("Client {} is present in DB with ID {}. "
                  "Proceeding to update existing entry".format(i_client['name'], cid))
        else:   # else add new entry
            loadsingleclientinfo(dbconfig, i_client)
    return


def loadsingleclientinfo(dbconfig: dict, data: dict, add_type=-1):
    """add single client with info provided as dictionary
    add_type == 1 for add client only
    add_type == 2 for add address only
    add_type == 3 for add identity only"""

    if add_type == 1:  # add client only
        addclient(dbconfig, data)
    elif add_type == 2:  # add address only
        addaddress(dbconfig, data)
    elif add_type == 3:  # add identity only
        addidentity(dbconfig, data)
    else:   # add all client, address and identity
        addclient(dbconfig, data)
        addaddress(dbconfig, data)
        addidentity(dbconfig, data)
    return






