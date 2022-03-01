import pandas as pd



class PySQL:
    def __init__(self, dbconfig):
        self.DBname = dbconfig['database']
        # SQL connection properties in dictionary
        self.dbconfig = dbconfig
        # query and query arguments (change for different query calls)
        self.query = ''
        self.query_args = None
        self.query_flag = None
        # get info on all tables (table name, column names) in db
        self.tables = []
        self._get_tables()

    def _get_tables(self):
        """get all tables associated with DB using MySQl connector"""

        # get DB table info
        self.query = ("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE "
                      "TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = %(db_name)s")
        self.query_args = {'db_name': self.DBname}
        table_info = getinfo(self, tables=True)

        # create PySQltable objects for each table and create list of table objects
        if table_info['table_names']:
            for i_table in table_info['table_names']:
                i_table_info = {'database': self.DBname, 'table_name': i_table, 'dbconfig': self.dbconfig}
                table_obj = PySQLtable(self, i_table_info)
                self.tables.append(table_obj)

    @staticmethod
    def _read_from_file(file_name=None):
        """read client info from file to dataframe"""

        # write_flag = False
        # read excel file with client data into pandas
        if file_name is not None:
            df = pd.read_excel(file_name, 'info', engine='openpyxl')
        else:
            df = None

        # fill nan values (for non NN columns in db) with appropriate replacement
        if df is not None:
            df['house_num'].fillna('none', inplace=True)
            df['locality'].fillna('none', inplace=True)

            # get first and last names from full name
            firstname = [iname.split()[0] for iname in df['name']]
            lastname = [iname.split()[1] for iname in df['name']]
            df = df.assign(firstname=pd.Series(firstname))
            df = df.assign(lastname=pd.Series(lastname))

            # convert street_num to string
            df['street_num'] = df['street_num'].map(str)

        return df

    def _reset_query_flag(self):
        """reset query flag to None before running new queries if flag is not None"""

        if self.query_flag is not None:
            self.query_flag = None
            print('Query flag reset to None')
        else:
            print('Query flag is already None')

    def _last_item_id(self, id_col):
        """get last id (biggest) from DB. Usually used to client id to new added entries"""

        # search db for latest clientid
        self._reset_query_flag()
        self.query = "SELECT {} FROM {}.clients".format(id_col, self.DBname)
        db_info = getinfo(self, id_only=True)

        if db_info is not None:
            if db_info['id']:
                large_id = max(db_info['id'])
            else:
                print('No previous existing ID. Initializing new ID from 1001.')
                large_id = 1000
        else:
            large_id = None
        return large_id

    def _assign_id(self, data: object, id_col):
        """assign client ids to new clients from client info file"""

        # search db for latest clientid
        large_id = self._last_item_id(id_col=id_col)

        # add client ids to new clients
        if large_id is not None:
            nrows = data.shape[0]
            large_id += 1
            new_ids = [large_id + irow for irow in range(0, nrows)]
            data = data.assign(id=pd.Series(new_ids))
        else:
            print('Could not access database to get existing IDs: Assign IDs manually \n')
        return data

    def enter_data(self, file_name=None, table_name=None):
        """enter data in file_name to all tables in table_name"""

        if file_name is not None and table_name is not None:
            data = self._read_from_file(file_name)
            # add client ID to new data
            data = self._assign_id(data, id_col='clientid')
            if isinstance(table_name, list):
                for i_table in table_name:
                    # add relevant to each table in db
                    tab_obj = [j_table for j_table in self.tables if j_table.name == i_table]
                    if tab_obj:
                        tab_obj = tab_obj[0]
                        print("Adding data to table {} in current DB {}".format(tab_obj.name, self.DBname))
                        tab_obj.add_data(data)
                    else:
                        tab_obj = None
                        print('Table {} is not present in current DB {}. Available tables are:'.format(table_name, self.DBname))
                        for k_table in self.tables:
                            print(format(k_table.name))
                        continue
            elif table_name == 'all':
                # add data to all tables in db
                for j_table in self.tables:
                    print("Adding data to table {} in current DB {}".format(j_table.name, self.DBname))
                    j_table.add_data(data)
            else:
                # add relevant data to single table in db
                tab_obj = [j_table for j_table in self.tables if j_table.name == table_name]
                if tab_obj:
                    tab_obj = tab_obj[0]
                    print("Adding data to table {} in current DB {}".format(tab_obj.name, self.DBname))
                    tab_obj.add_data(data)
                else:
                    tab_obj = None
                    print('Table {} is not present in current DB {}. Available tables are:'.format(table_name,
                                                                                                   self.DBname))
                    for k_table in self.tables:
                        print(format(k_table.name))
        else:
            print('File name/Table name to enter data is empty')

    def check_db(self, query, info: dict, get_client=False, get_address=False, get_identity=False):
        """check if given client part of DB based on given info (name/pan/client id)
            and return all details of said client"""

        self._reset_query_flag()
        self_query = query
        self.query_args = info
        dbinfo = getinfo(self, client=get_client, address=get_address, identity=get_identity)

        # if get_address and get_password:
        #     if qtype == 1:  # get info with clientid
        #         self.query = ("SELECT * FROM clients LEFT JOIN (address, identity) "
        #                       "ON (clients.clientid=address.clientid AND clients.clientid=identity.clientid AND \
        #                       clients.clientid = %(clientid)s)")
        #     elif qtype == 2:  # get info using name
        #         self.query = ("SELECT * FROM clients LEFT JOIN (address, identity) "
        #                       "ON (clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
        #                       "(clients.firstname = %(firstname)s OR clients.lastname = %(lastname)s)")
        #     elif qtype == 3:  # get info using pan
        #         self.query = ("SELECT * FROM clients LEFT JOIN (address, identity) ON "
        #                       "(clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
        #                       "clients.pan = %(pan)s")
        #     else:  # get info using clientid, name or pan
        #         self.query = ("SELECT * FROM clients LEFT JOIN (address, identity) ON "
        #                       "(clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
        #                       "(clients.clientid = %(clientid)s OR clients.firstname = %(firstname)s OR "
        #                       "clients.lastname = %(lastname)s OR clients.pan = %(pan)s)")
        #     self._reset_query_flag()
        #     self.query_args = info
        #     dbinfo = getinfo(self, address=True, identity=True)
        # elif get_address and not get_password:
        #     if qtype == 1:  # get info with clientid
        #         self.query = ("SELECT * FROM clients LEFT JOIN address "
        #                       "ON (clients.clientid=address.clientid AND clients.clientid = %(clientid)s) "
        #                       "WHERE address.streetname is NOT NULL OR address.streetnumber is NOT NULL OR "
        #                       "address.housenum is NOT NULL OR address.locality is NOT NULL OR "
        #                       "address.city is NOT NULL OR address.state is NOT NULL")
        #     elif qtype == 2:  # get info using name
        #         self.query = ("SELECT * FROM clients LEFT JOIN address "
        #                       "ON (clients.clientid=address.clientid AND (clients.firstname = %(firstname)s OR "
        #                       "clients.lastname = %(lastname)s) WHERE address.streetname is NOT NULL OR "
        #                       "address.streetnumber is NOT NULL OR address.housenum is NOT NULL OR "
        #                       "address.locality is NOT NULL OR address.city is NOT NULL OR address.state is NOT NULL")
        #     elif qtype == 3:  # get info using pan
        #         self.query = ("SELECT * FROM clients LEFT JOIN address "
        #                       "ON (clients.clientid=address.clientid AND clients.pan = %(pan)s WHERE "
        #                       "address.streetname is NOT NULL OR address.streetnumber is NOT NULL OR "
        #                       "address.housenum is NOT NULL OR address.locality is NOT NULL OR "
        #                       "address.city is NOT NULL OR address.state is NOT NULL")
        #     else:  # get info using clientid, name or pan
        #         self.query = ("SELECT * FROM clients LEFT JOIN address "
        #                       "ON (clients.clientid=address.clientid AND "
        #                       "(clients.clientid = %(clientid)s OR clients.firstname = %(firstname)s OR "
        #                       "clients.lastname = %(lastname)s OR clients.pan = %(pan)s) WHERE "
        #                       "address.streetname is NOT NULL OR address.streetnumber is NOT NULL OR "
        #                       "address.housenum is NOT NULL OR address.locality is NOT NULL OR "
        #                       "address.city is NOT NULL OR address.state is NOT NULL")
        #     self._reset_query_flag()
        #     self.query_args = info
        #     dbinfo = getinfo(self, address=True)
        #     # remove all row entries corresponding to a None entry (SQL output is NULL for respective row)
        #     # remove_row()
        # else:
        #     if qtype == 1:  # check using client ID
        #         self.query = ("SELECT firstname, lastname, clientid, pan FROM taxdata.clients "
        #                       "WHERE clientid = %(clientid)s")
        #     elif qtype == 2:  # get info using name
        #         self.query = ("SELECT firstname, lastname, clientid, pan FROM taxdata.clients "
        #                       "WHERE firstname = %(firstname)s OR lastname = %(lastname)s")
        #     elif qtype == 3:  # get info using pan
        #         self.query = ("SELECT firstname, lastname, clientid, pan FROM taxdata.clients "
        #                       "WHERE pan = %(pan)s")
        #     else:  # check using all of the above
        #         self.query = ("SELECT firstname, lastname, clientid, pan FROM taxdata.clients "
        #                       "WHERE firstname = %(firstname)s OR lastname = %(lastname)s OR "
        #                       "pan = %(pan)s OR clientid = %(clientid)s")
        #     self._reset_query_flag()
        #     self.query_args = info
        #     dbinfo = getinfo(self)

        return dbinfo

    def change_table_entry(self, query, query_args):
        """call query_db to add/update entry in table"""

        self.query = query
        self.query_args = query_args
        self._reset_query_flag()
        self.query_flag = query_db(self)
        return self


class PySQLtable:
    def __init__(self, db_obj, init):
        self.DBname = init['database']
        self.name = init['table_name']
        self.DB = db_obj
        # get info on all columns in table
        self.column_names = None
        self.column_dtype = None
        self.is_null = None
        self.column_default = None
        self.columns = 0
        self._get_columns()
        if init.get('key') is not None:
            self.keys = init['key']
        else:
            self.keys = None
        if init.get('foreign_key') is not None:
            self.foreign_key = init['foreign_key']
        else:
            self.foreign_key = None

    def _get_columns(self):
        """get all column names for listed tables in DB"""

        # get column names, column type, column nullablity and column default
        self.DB.query = ("SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, COLUMN_DEFAULT, IS_NULLABLE, COLUMN_KEY "
                        "FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = %(table_name)s")
        self.DB.query_args = {'table_name': self.name}
        column_info = getinfo(self.DB, columns=True)
        self.column_names = column_info['column_names']
        self.column_dtype = column_info['column_dtype']
        self.is_null = column_info['is_null']
        self.column_default = column_info['default']
        self.columns = len(self.column_names)

    @staticmethod
    def _list2dict(info_dict: dict) -> list:
        """convert dictionary of list to list of dictionaries for info obtained from db"""

        new_list, new_dict = [], {}
        nvals = [len(info_dict[key]) for key, _ in info_dict.items() if info_dict[key]]  # size of new final list
        if any(nvals):
            nvals = max(nvals)
        else:
            nvals = 0

        for ival in range(0, nvals):
            for key, _ in info_dict.items():
                if info_dict[key]:
                    new_dict[key] = info_dict[key][ival]
                else:
                    new_dict[key] = ''
            new_list.append(new_dict)
        return new_list

    def _compare_info(self, info: dict, dbinfo: dict, check_name=False, check_id=False, check_address=False):
        """compare given information with information obtained from db and see what the difference is"""

        name_check = False
        id_check = False
        pan_check = False
        if self.name == 'clients':
            if info['firstname'] == dbinfo['firstname'] and info['lastname'] == dbinfo['lastname']:
                name_check = True
            if info['clientid'] == dbinfo['clientid']:
                id_check = True
            if info['pan'] == dbinfo['pan']:
                pan_check = True

        if self.name == 'identity':
            if info['clientid'] == dbinfo['clientid']:
                id_check = True
            if info['pan'] == dbinfo['pan']:
                pan_check = True

        add_check = True
        if self.name == 'address':
            if info['clientid'] == dbinfo['clientid']:
                id_check = True
            if info['street_name'] != dbinfo['streetname'] or info['street_num'] != dbinfo['streetnumber'] or \
                    info['house_num'] != dbinfo['housenum'] or info['locality'] != dbinfo['locality'] or \
                    info['city'] != dbinfo['city'] or info['state'] != dbinfo['state'] or \
                    info['pin'] != dbinfo['pin']:
                add_check = False

        return name_check, id_check, pan_check, add_check

    # def _update_cost(self, db_obj: PySQL, dbinfo: dict, data: dict):
    #     """check address fields that are different and update only these fields"""
    #
    #     # check address fields that are different
    #     up_query = None
    #     if data['cost'] != dbinfo['cost']:
    #         # update to_date to reflect current timestamp
    #         up_query = ("UPDATE {}.{} SET {}.to_date = CURRENT_TIMESTAMP WHERE {}.id = %(id)s".format(self.DBname,
    #                                                                                                   self.name,
    #                                                                                                   self.name,
    #                                                                                                   self.name))
    #         db_obj = db_obj.change_table_entry(up_query, data)
    #         # add new cost entry with from_date = CURRENT_TIMESTAMP
    #         self._add_single_entry(db_obj, data, add_type=1)
    #     if db_obj.query_flag:
    #         print("Cost of `{}` changed from {} to {} in {}".format(data['description'], dbinfo['cost'], data['cost'],
    #                                                                 self.name))
    #     else:
    #         print("Cost of `{}` NOT CHANGED from {} in {}".format(data['description'], dbinfo['cost'], self.name))
    #
    #     return
    #
    # def _update_entry(self, db_obj:PySQL, dbinfo: dict, data: dict, entry_type=-1):
    #     """update a single/single type of entry in db
    #     entry_type == 1 for update cost only"""
    #
    #     if entry_type == 1:  # update cost only (items)
    #         self._update_cost(db_obj, dbinfo, data)
    #     else:
    #         self._update_cost(db_obj, dbinfo, data)
    #         # update entries in other tables
    #     return
    #
    # def _add_client(self, query_args: dict):
    #     """call db_obj.add_item to add entry to relevant table"""
    #
    #     query = ("INSERT INTO {}.{} "
    #              "(clientid, firstname, lastname, pan) "
    #              "VALUES (%(client_id)s, %(firstname)s, %(lastname)s, %(pan)s)".format(self.DBname, self.name))
    #     self.DB = self.DB.change_table_entry(query, query_args)
    #     if self.DB.query_flag:
    #         print("Entry with id `{}` and name `{} {}` added to {} in {}".format(query_args['client_id'],
    #                                                                              query_args['firstname'],
    #                                                                              query_args['lastname'],
    #                                                                              self.name, self.DBname))
    #     else:
    #         print("Entry with name {} {} NOT added to {}".format(query_args['firstname'], query_args['lastname'], self.name))
    #
    #
    # def _add_address(self, query_args: dict):
    #     """add client address details to db"""
    #
    #     query = ("INSERT INTO {}.address "
    #              "(clientid, streetnumber, streetname, housenum, locality, city, state, pin) "
    #              "VALUES (%(client_id)s, %(street_num)s, %(street_name)s, %(house_num)s, %(locality)s, %(city)s, "
    #              "%(state)s, %(pin)s)".format(self.DBname))
    #     flag = querydb(dbconfig, add_address, details)
    #     return flag
    #
    # def addidentity(dbconfig: dict, details: dict):
    #     """add client identity details to db"""
    #
    #     add_identity = ("INSERT INTO {}.identity "
    #                     "(clientid, pan, portalpass) "
    #                     "VALUES (%(client_id)s, %(pan)s, %(portalpass)s)".format(dbconfig['database']))
    #     flag = querydb(dbconfig, add_identity, details)
    #     return flag

    # def _add_single_entry(self, data: dict, add_type=-1):
    #     """add single client with info provided as dictionary
    #     add_type == 1 for add client only
    #     add_type == 2 for add address only
    #     add_type == 3 for add identity only"""
    #
    #     if add_type == 1:  # add client only
    #         self._add_client(data)
    #     elif add_type == 2:  # add address only
    #         addaddress(dbconfig, data)
    #     elif add_type == 3:  # add identity only
    #         addidentity(dbconfig, data)
    #     else:   # add all client, address and identity
    #         addclient(dbconfig, data)
    #         addaddress(dbconfig, data)
    #         addidentity(dbconfig, data)

    # (self, db_obj: PySQL, data, add_type=-1):
    #     """add a single new entry to existing table in existing DB
    #     add_type == 1 for add item only"""
    #
    #     if add_type == 1:  # add item only
    #         self._add_item(data)
    #     else:
    #         self._add_item(data)
    #         # add items to other tables as well
    #     return

    def _check_table(self, info: dict):
        """check table in db for existing entry"""

        db_info = None
        if self.name == 'clients':
            query = ("SELECT firstname, lastname, clientid, pan FROM {}.clients "
                     "WHERE firstname = %(firstname)s OR lastname = %(lastname)s OR "
                     "pan = %(pan)s OR clientid = %(clientid)s".format(self.DBname))
            db_info = self.DB.check_db(query, info, get_client=True)
        elif self.name == 'address':
            query = ("SELECT streetnumber, streetname, housenum, locality, city, state, pin "
                     "FROM address LEFT JOIN clients ON (clients.clientid=address.clientid AND "
                     "(clients.clientid = %(clientid)s OR clients.firstname = %(firstname)s OR "
                     "clients.lastname = %(lastname)s OR clients.pan = %(pan)s)")
            db_info = self.DB.check_db(query, info, get_address=True)
        elif self.name == 'identity':
            query = ("SELECT pan, clientid, portalpass FROM identity LEFT JOIN clients ON "
                     "(clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
                     "(clients.clientid = %(clientid)s OR clients.firstname = %(firstname)s OR "
                     "clients.lastname = %(lastname)s OR clients.pan = %(pan)s)")
            db_info = self.DB.check_db(query, info, get_identity=True)
        else:
            print("Table {} is not present in DB {}".format(self.name, self.DBname))
        return db_info

    def add_data(self, data):
        """load client info from dataframe to db"""

        data_list = data.to_dict('records')
        for idx, i_entry in enumerate(data_list):
            # check if new entry in db (same name/pan)
            db_info = self._check_table(i_entry)
            info_list = None
            if db_info:
                info_list = self._list2dict(db_info)
            if info_list is not None and info_list:
                name_check, _, _, _ = self._compare_info(i_entry, info_list[0])
            else:
                name_check = False
    #         if item_check:  # if present, only update existing entry (cost) or return error
    #             print("Client {} is present in DB with ID {}. "
    #                   "Proceeding to update existing entry".format(i_client['name'], info_list[0]['clientid']))
    #             # change client id to one obtained from db
    #             i_client['clientid'] = info_list[0]['clientid']
    #             # get existing client info (pan,address) using client info from db
    #             db_info = check_db(dbconfig, i_entry, qtype=1, get_address=True)
    #             info_list = self._list2dict(db_info)
    #             # check if same address in DB
    #             _, _, _, add_check = compare_info(i_entry, info_list[0], check_address=True)
    #             if not add_check:
    #                 # self._update_entry(db_obj, info_list[0], i_entry)  # update DB if cost is not same
    #             else:
    #                 print("{} with ID {} has same cost {} in DB. "
    #                       "No changes made".format(i_entry['description'], i_entry['id'], info_list[0]['cost']))
    #         else:  # else add new entry
    #             self._add_single_entry(db_obj, i_entry)

