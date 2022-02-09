import pandas as pd
from query import querydb, check_db, getinfo
import collections


def last_client_id(dbconfig: dict):
    """get last client id (biggest) from DB. Usually used to assign client id to new added clients"""

    # search db for latest clientid
    query = ("SELECT clientid FROM {}.clients".format(dbconfig['database']))
    db_info = getinfo(dbconfig, query, id_only=True)

    if db_info is not None:
        large_id = max(db_info['clientid'])
    else:
        large_id = None

    return large_id


def assignid(dbconfig: dict, data: object) -> object:
    """assign client ids to new clients from client info file"""

    # search db for latest clientid
    large_id = last_client_id(dbconfig)

    # add client ids to new clients
    if large_id is not None:
        nrows = data.shape[0]
        large_id += 1
        new_client_ids = [large_id + irow for irow in range(0, nrows)]
        data = data.assign(clientid=pd.Series(new_client_ids))
    else:
        print('Could not access database to get existing client ID: Assign client ID manually \n')
    return data


def compare_info(info: dict, dbinfo: dict, check_name=True, check_id=False, check_address=False):
    """compare given information with information obtained from db and see what the difference is"""

    name_check = False
    if check_name:
        if info['firstname'] == dbinfo['firstname'][0] and info['lastname'] == dbinfo['lastname'][0]:
            name_check = True

    id_check = False
    pan_check = False
    if check_id:
        # client id check
        if info['clientid'] == dbinfo['clientid'][0]:
            id_check = True
        # pan check
        if info['pan'] == dbinfo['pan'][0]:
            pan_check = True

    add_check = True
    if check_address:
        if info['streetname'] != dbinfo['streetname'][0] or info['streetnumber'] != dbinfo['streetnumber'][0] or \
                info['housenum'] != dbinfo['housenum'][0] or info['locality'] != dbinfo['locality'][0] or \
                info['city'] != dbinfo['city'][0] or info['state'] != dbinfo['state'][0] or \
                info['pin'] != dbinfo['pin'][0]:
            add_check = False

    return name_check, id_check, pan_check, add_check


def list2dict():
    """convert dictionary of list to list of dictionaries for info obtained from db"""
    return


def loadclientinfo(data: object, dbconfig=None):
    """load client info from dataframe to db"""

    # assign client id to new clients
    data = assignid(dbconfig, data)

    client_list = data.to_dict('records')
    for i_client in client_list:
        # check if new client in db (same name/pan)
        db_info = check_db(dbconfig, i_client)
        name_check, _, _, _ = compare_info(i_client, db_info)
        if name_check:     # if present, only update existing entry (address) or return error
            print("Client {} is present in DB with ID {}. "
                  "Proceeding to update existing entry".format(i_client['name'], db_info['clientid']))
        #     # check if same address in DB
        #     # client_add = query_address(dbconfig, client_info)
        #     # update_db(i_client, dbconfig)
        else:   # else add new entry
            loadsingleclientinfo(dbconfig, i_client)
    return


def addclient(dbconfig: dict, details: dict):
    """add client name details to db"""

    add_client = ("INSERT INTO {}.clients "
                  "(clientid, firstname, lastname, pan) "
                  "VALUES (%(client_id)s, %(firstname)s, %(lastname)s, %(pan)s)".format(dbconfig['database']))
    flag = querydb(dbconfig, add_client, details)
    return flag


def addaddress(dbconfig: dict, details: dict):
    """add client address details to db"""

    add_address = ("INSERT INTO {}.address "
                   "(clientid, streetnumber, streetname, housenum, locality, city, state, pin) "
                   "VALUES (%(client_id)s, %(street_num)s, %(street_name)s, %(house_num)s, %(locality)s, %(city)s, "
                   "%(state)s, %(pin)s)".format(dbconfig['database']))
    flag = querydb(dbconfig, add_address, details)
    return flag


def addidentity(dbconfig: dict, details: dict):
    """add client identity details to db"""

    add_identity = ("INSERT INTO {}.identity "
                    "(clientid, pan, portalpass) "
                    "VALUES (%(client_id)s, %(pan)s, %(portalpass)s)".format(dbconfig['database']))
    flag = querydb(dbconfig, add_identity, details)
    return flag


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