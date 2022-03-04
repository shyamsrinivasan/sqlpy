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

    flag = updatedb(dbconfig, up_fields, up_query, data, address=True)
    return


def update_client(dbconfig: dict, dbinfo: dict, data: dict):
    """check if fields in client table are different and change only allowed fields"""

    up_fields = [False, False, False]
    up_query = {'clientid': '', 'firstname': '', 'lastname': '', 'pan': ''}
    if data['clientid'] != dbinfo['clientid']:
        # same name but different client id -> change to same client id
        up_fields[0] = True
        up_query['clientid'] = ("UPDATE {}.clients SET clientid = %(clientid)s WHERE clients.firstname = %(firstname)s "
                                "AND clients.lastname = %(lastname)s".format(dbconfig['database']))

    if data['firstname'] != dbinfo['firstname']:
        up_fields[1] = True
        up_query['firstname'] = ("UPDATE {}.clients SET firstname = %(firstname)s "
                                "WHERE clients.clientid = %(clientid)s".format(dbconfig['database']))

    if data['lastname'] != dbinfo['lastname']:
        up_fields[2] = True
        up_query['lastname'] = ("UPDATE {}.clients SET lastname = %(lastname)s "
                                "WHERE clients.clientid = %(clientid)s".format(dbconfig['database']))

    if data['pan'] != dbinfo['pan']:
        print('PAN cannot be changed')

    if all(up_fields):
        up_query['all'] = ("UPDATE {}.clients SET firstname = %(firstname)s, lastname = %(lastname)s "
                           "WHERE clients.clientid = %(clientid)s".format(dbconfig['database']))

    flag = updatedb(dbconfig, up_fields, up_query, data, client=True)
    return


def update_identity(dbconfig: dict, dbinfo: dict, data: dict):
    """check if fields in identity are same and change only fields that differ"""

    up_fields = [False]
    up_query = {'clientid': '', 'portalpass': ''}

    if data['portalpass'] != dbinfo['portalpass']:
        up_fields[0] = True
        up_query['portalpass'] = ("UPDATE {}.identity SET portalpass = %(portalpass)s "
                                  "WHERE clients.clientid = %(clientid)s".format(dbconfig['database']))
        up_query['all'] = up_query['portalpass']

    flag = updatedb(dbconfig, up_fields, up_query, data)
    return


def update1entry(dbconfig: dict, dbinfo: dict, data: dict, entry_type=1):
    """update a single/single type of entry in db
    entry_type == 1 for update client only
    entry_type == 2 for update address only
    entry_type == 3 for update identity (password) only"""

    if entry_type == 1:  # update address only
        update_address(dbconfig, dbinfo, data)
    elif entry_type == 2:  # add client only
        update_client(dbconfig, dbinfo, data)
    elif entry_type == 3:  # add identity only
        update_identity(dbconfig, dbinfo, data)
    else:   # add all client, address and identity
        update_client(dbconfig, dbinfo, data)
        update_address(dbconfig, dbinfo, data)
        update_identity(dbconfig, dbinfo, data)
    return


def add_column(dbconfig: dict, data: dict):
    """add column to existing table in DB"""

    # query = ("ALTER TABLE {} alter_option".format())
    # ALTER TABLE table_name ADD column_name column_dtype column_is_null column_default/other_value
    # ALTER TABLE t2 ADD c INT UNSIGNED NOT NULL AUTO_INCREMENT
    return
