from query import updatedb


def update_address(dbconfig: dict, dbinfo: dict, data: dict):
    """check address fields that are different and update only these fields"""

    # check address fields that are different
    up_fields = [False, False, False, False, False, False, False]
    up_query = {'streetnumber': '', 'streetname': '', 'housenum': '', 'locality': '', 'city': '', 'state': '',
                'pin': ''}
    if data['street_num'] != dbinfo['streetnumber']:
        up_fields[0] = True
        up_query['streetnumber'] = ("UPDATE {}.address SET streetnumber = %(street_num)s "
                                    "WHERE address.clientid = %(clientid)s".format(dbconfig['database']))

    if data['street_name'] != dbinfo['streetname']:
        up_fields[1] = True
        up_query['streetname'] = ("UPDATE {}.address SET streetname = %(street_name)s "
                                  "WHERE address.clientid = %(clientid)s".format(dbconfig['database']))

    if data['house_num'] != dbinfo['housenum']:
        up_fields[2] = True
        if data['house_num'] == 'none':
            up_query['housenum'] = ("UPDATE {}.address SET housenum = NULL "
                                    "WHERE address.clientid = %(clientid)s".format(dbconfig['database']))
        else:
            up_query['housenum'] = ("UPDATE {}.address SET housenum = %(house_num)s "
                                    "WHERE address.clientid = %(clientid)s".format(dbconfig['database']))

    if data['locality'] != dbinfo['locality']:
        up_fields[3] = True
        if data['locality'] == 'none':
            up_query['locality'] = ("UPDATE {}.address SET locality = NULL "
                                    "WHERE address.clientid = %(clientid)s".format(dbconfig['database']))
        else:
            up_query['locality'] = ("UPDATE {}.address SET locality = %(locality)s "
                                    "WHERE address.clientid = %(clientid)s".format(dbconfig['database']))

    if data['city'] != dbinfo['city']:
        up_fields[4] = True
        up_query['city'] = ("UPDATE {}.address SET city = %(city)s "
                            "WHERE address.clientid = %(clientid)s".format(dbconfig['database']))

    if data['state'] != dbinfo['state']:
        up_fields[5] = True
        up_query['state'] = ("UPDATE {}.address SET state = %(state)s "
                             "WHERE address.clientid = %(clientid)s".format(dbconfig['database']))

    if data['pin'] != dbinfo['pin']:
        up_fields[6] = True
        up_query['pin'] = ("UPDATE {}.address SET pin = %(pin)s "
                           "WHERE address.clientid = %(clientid)s".format(dbconfig['database']))

    if all(up_fields):
        up_query['all'] = ("UPDATE {}.address SET streetnumber = %(street_num)s, streetname = %(street_name)s, "
                           "housenum = %(house_num)s, locality = %(locality)s, city = %(city)s, state = %(state)s, "
                           "pin = %(pin)s WHERE address.clientid = %(clientid)s".format(dbconfig['database']))

    updatedb(dbconfig, up_fields, up_query, data)
    return


def update_client(dbconfig: dict, data: dict):
    update_cl = ("UPDATE tablename SET colname = colvalue")
    # update_db(dbconfig, update_cl, data)
    return


def update_identity(dbconfig: dict, data: dict):
    # steps to update client info
    # 1. check if info (identity) in db is same as provided info
    # 2. if TRUE - do not update
    # 3. else (FALSE) - update db entries
    update_id = ("UPDATE")
    # update_db(dbconfig, update_id, data)
    return


def update1entry(dbconfig: dict, dbinfo: dict, data: dict, entry_type=1):
    """update a single/single type of entry in db
    entry_type == 1 for update client only
    entry_type == 2 for update address only
    entry_type == 3 for update identity (password) only"""

    if entry_type == 1:  # update address only
        update_address(dbconfig, dbinfo, data)
    elif entry_type == 2:  # add client only
        update_client(dbconfig, data)
    elif entry_type == 3:  # add identity only
        update_identity(dbconfig, data)
    else:   # add all client, address and identity
        update_client(dbconfig, data)
        update_address(dbconfig, dbinfo, data)
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



