from query import updatedb


def update_address(dbconfig: dict, dbinfo: dict, data: dict):
    """check address fields that are different and update only these fields"""

    # check address fields that are different
    up_fields = [False, False, False, False, False, False, False]
    up_query = {'streetnumber': '', 'streetname': '', 'housenum': '', 'locality': '', 'city': '', 'state': '',
                'pin': ''}
    if data['streetnumber'] != dbinfo['streetnumber']:
        up_fields[0] = True
        up_query['streetnumber'] = ("UPDATE {}.address SET streetnumber = %(streetnumber)s".format(dbconfig))

    if data['streetname'] != dbinfo['streetname']:
        up_fields[1] = True
        up_query['streetname'] = ("UPDATE {}.address SET streetname = %(streetname)s".format(dbconfig))

    if data['housenum'] != dbinfo['housenum']:
        up_fields[2] = True
        up_query['housenum'] = ("UPDATE {}.address SET housenum = %(housenum)s".format(dbconfig))

    if data['locality'] != dbinfo['locality']:
        up_fields[3] = True
        up_query['locality'] = ("UPDATE {}.address SET locality = %(locality)s".format(dbconfig))

    if data['city'] != dbinfo['city']:
        up_fields[4] = True
        up_query['city'] = ("UPDATE {}.address SET city = %(city)s".format(dbconfig))

    if data['state'] != dbinfo['state']:
        up_fields[5] = True
        up_query['state'] = ("UPDATE {}.address SET state = %(state)s".format(dbconfig))

    if data['pin'] != dbinfo['pin']:
        up_fields[6] = True
        up_query['pin'] = ("UPDATE {}.address SET pin = %(pin)s".format(dbconfig))

    # query = ("UPDATE tablename SET colname = colvalue")
    updatedb(dbconfig, up_query, data)
    return


def update_client(dbconfig: dict, data: dict):
    update_cl = ("UPDATE tablename SET colname = colvalue")
    # update_db(dbconfig, update_cl, data)
    return


def update_identity(dbconfig: dict, data: dict):
    update_id = ("UPDATE")
    # update_db(dbconfig, update_id, data)
    return


def updatesingleentry(dbconfig: dict, data: dict, entry_type=1):
    """update a single/single type of entry in db
    entry_type == 1 for update client only
    entry_type == 2 for update address only
    entry_type == 3 for update identity (password) only"""

    if entry_type == 1:  # add address only
        update_address(dbconfig, data)
    elif entry_type == 2:  # add client only
        update_client(dbconfig, data)
    elif entry_type == 3:  # add identity only
        update_identity(dbconfig, data)
    else:   # add all client, address and identity
        update_client(dbconfig, data)
        update_address(dbconfig, data)
        update_identity(dbconfig, data)
    return


# def check_update(dbconfig: dict, info: dict):
#     """check if current entries for existing clients are same as one provided. If not, update entry.
#     Update only entries that are different"""
#
#     # check client info using
#     query = ("SELECT firstname, lastname FROM {}.clients")
#     # check address info
#     # check identity info
#
#     return



