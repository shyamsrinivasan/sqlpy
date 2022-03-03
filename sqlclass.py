import pandas as pd
from accessdb import getinfo, query_db


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
        # else:
        #     print('Query flag is already None')

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
            data = data.assign(clientid=pd.Series(new_ids))
        else:
            print('Could not access database to get existing IDs: Assign IDs manually \n')
        return data

    def enter_data(self, file_name=None, table_name=None):
        """enter data in file_name to all tables in table_name"""

        if file_name is not None:
            data = self._read_from_file(file_name)
            # add client ID to new data
            data = self._assign_id(data, id_col='clientid')
            if table_name is not None:
                # add data only to selected tables
                print('Adding data to given tables only')
            else:
                # add data to all tables in db one table at a time
                # add data to parent table (clients) first
                tab_obj = [j_table for j_table in self.tables if j_table.name == 'clients'][0]
                print("Adding data to table {} in current DB {}".format(tab_obj.name, self.DBname))
                # check if data present in clients table. Change client id if present
                data_list = data.to_dict('records')     # convert data df to list of dict
                for i_data in data_list:
                    id_check, name_check, pan_check, add_check, info_list = tab_obj.check_client(i_data)
                    if info_list is not None and info_list:
                        if (name_check or pan_check) and not id_check:
                            i_data['clientid'] = info_list['clientid']
                tab_obj.add_data(data_list)
                # add data to other (child) tables
                for j_table in self.tables:
                    if j_table.name != 'clients':
                        print("Adding data to table {} in current DB {}".format(j_table.name, self.DBname))
                        j_table.add_data(data_list)
                    else:
                        continue
        else:
            print('File name to enter data is empty')

    #         if isinstance(table_name, list):
    #             for i_table in table_name:
    #                 # add relevant to each table in db
    #                 tab_obj = [j_table for j_table in self.tables if j_table.name == i_table]
    #                 if tab_obj:
    #                     tab_obj = tab_obj[0]
    #                     print("Adding data to table {} in current DB {}".format(tab_obj.name, self.DBname))
    #                     tab_obj.add_data(data)
    #                 else:
    #                     tab_obj = None
    #                     print('Table {} is not present in current DB {}. Available tables are:'.format(table_name, self.DBname))
    #                     for k_table in self.tables:
    #                         print(format(k_table.name))
    #                     continue
    #         elif table_name == 'all':
    #
    #         else:
    #             # add relevant data to single table in db
    #             tab_obj = [j_table for j_table in self.tables if j_table.name == table_name]
    #             if tab_obj:
    #                 tab_obj = tab_obj[0]
    #                 print("Adding data to table {} in current DB {}".format(tab_obj.name, self.DBname))
    #                 tab_obj.add_data(data)
    #             else:
    #                 tab_obj = None
    #                 print('Table {} is not present in current DB {}. Available tables are:'.format(table_name,
    #                                                                                                self.DBname))
    #                 for k_table in self.tables:
    #                     print(format(k_table.name))
    #     else:
    #

    def change_table_entry(self, query, query_args):
        """call query_db to add/update entry in table"""

        self.query = query
        self.query_args = query_args
        self._reset_query_flag()
        self.query_flag = query_db(self)
        return self

    def get_table_entry(self, query, query_args, id_only=False, client=False, address=False, identity=False):
        """call get_info to get entry from db using SELECT"""

        self.query = query
        self.query_args = query_args
        self._reset_query_flag()
        dbinfo = getinfo(self, id_only=id_only, client=client, address=address, identity=identity)
        return dbinfo


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

    def add_data(self, data):
        """load client info from dataframe to db"""

        # data_list = data.to_dict('records')
        for idx, i_entry in enumerate(data):
            # check if new entry in db (same name/pan)
            id_check, name_check, pan_check, add_check, info_list = self.check_client(i_entry)
            # db_info = self._check_table(i_entry)
            # info_list = None
            # id_check, name_check, pan_check, add_check = False, False, False, True
            # if db_info:
            #     info_list = self._list2dict(db_info)
            if info_list is not None and info_list:
                # name_check, id_check, pan_check, add_check = self._compare_info(i_entry, info_list[0])
                if name_check and id_check and pan_check:
                    print("Client {} {} is present in DB with ID:{} and PAN:{}. "
                          "Proceeding to update existing entry".format(i_entry['firstname'], i_entry['lastname'],
                                                                       info_list['clientid'],
                                                                       info_list['pan']))
                else:
                    if name_check and not pan_check:
                        print("Client {} {} is present in DB with different PAN:{}".format(i_entry['firstname'],
                                                                                           i_entry['lastname'],
                                                                                           info_list['pan']))
                        if info_list['pan']:
                            i_entry['pan'] = info_list['pan']
                        # may be update PAN?
                    elif name_check and not id_check:
                        print("Client {} {} is present in DB with different ID:{}".format(i_entry['firstname'],
                                                                                          i_entry['lastname'],
                                                                                          info_list['clientid']))
                        # change client id to one obtained from db
                        i_entry['clientid'] = info_list['clientid']
                    else:
                        print("Client {} {} is NOT present in DB with ID:{} and PAN:{}. "
                              "Proceeding to add entry".format(i_entry['firstname'], i_entry['lastname'],
                                                               i_entry['clientid'], i_entry['pan']))
                        self._add_single_table_entry(i_entry)
                if id_check and not add_check:
                    print("Client {} {} is present in DB with ID:{} and different address. "
                          "Proceeding to update address".format(i_entry['firstname'], i_entry['lastname'],
                                                                i_entry['clientid']))
            else:
                print("Client {} {} is NOT present in table {}. "
                      "Proceeding to add entry".format(i_entry['firstname'], i_entry['lastname'], self.name))
                self._add_single_table_entry(i_entry)

    def _add_single_table_entry(self, entry_info):
        """add data to one table based on which table object calls method"""

        if self.name == 'clients':
            # add data to clients table
            query = ("INSERT INTO {}.{} "
                     "(clientid, firstname, lastname, pan) "
                     "VALUES (%(clientid)s, %(firstname)s, %(lastname)s, %(pan)s)".format(self.DBname, self.name))
            self.DB = self.DB.change_table_entry(query, entry_info)
            if self.DB.query_flag:
                print("Entry with id `{}` and name `{} {}` added to {} in {}".format(entry_info['clientid'],
                                                                                     entry_info['firstname'],
                                                                                     entry_info['lastname'],
                                                                                     self.name, self.DBname))
            else:
                print("Entry with name {} {} NOT added to {}".format(entry_info['firstname'], entry_info['lastname'],
                                                                     self.name))

        if self.name == 'address':
            # add data to address table
            query = ("INSERT INTO {}.{} "
                     "(clientid, streetnumber, streetname, housenum, locality, city, state, pin) "
                     "VALUES (%(clientid)s, %(street_num)s, %(street_name)s, %(house_num)s, %(locality)s, %(city)s, "
                     "%(state)s, %(pin)s)".format(self.DBname, self.name))
            self.DB = self.DB.change_table_entry(query, entry_info)
            if self.DB.query_flag:
                print("Entry with id `{}` and address `{} {}, {}, {}, {}-{}` "
                      "added to {} in {}".format(entry_info['clientid'], entry_info['street_num'],
                                                 entry_info['street_name'], entry_info['locality'], entry_info['city'],
                                                 entry_info['state'], entry_info['pin'], self.name, self.DBname))
            else:
                print("Entry with name {} {} and id {} NOT added to {}".format(entry_info['firstname'],
                                                                               entry_info['lastname'],
                                                                               entry_info['clientid'], self.name))
        if self.name == 'identity':
            # add data to identity table
            query = ("INSERT INTO {}.{} (clientid, pan, portalpass) "
                     "VALUES (%(clientid)s, %(pan)s, %(portalpass)s)".format(self.DBname, self.name))
            self.DB = self.DB.change_table_entry(query, entry_info)
            if self.DB.query_flag:
                print("Entry with id `{}` and PAN `{}` "
                      "added to {} in {}".format(entry_info['clientid'], entry_info['pan'], self.name, self.DBname))
            else:
                print("Entry with name {} {} and id {} NOT added to {}".format(entry_info['firstname'],
                                                                               entry_info['lastname'],
                                                                               entry_info['clientid'], self.name))

    def _check_table(self, info: dict):
        """check table in db for existing entry"""

        db_info = None
        if self.name == 'clients':
            query = ("SELECT firstname, lastname, clientid, pan FROM {}.clients "
                     "WHERE firstname = %(firstname)s OR lastname = %(lastname)s OR "
                     "pan = %(pan)s OR clientid = %(clientid)s".format(self.DBname))
            db_info = self.DB.get_table_entry(query, info, client=True)
        elif self.name == 'address':
            query = ("SELECT address.clientid, clients.firstname, clients.lastname, clients.pan, streetnumber, streetname, "
                     "housenum, locality, city, state, pin "
                     "FROM clients LEFT JOIN address ON (clients.clientid=address.clientid AND "
                     "(clients.clientid = %(clientid)s OR clients.firstname = %(firstname)s OR "
                     "clients.lastname = %(lastname)s OR clients.pan = %(pan)s)) WHERE address.streetname is NOT NULL "
                     "OR address.streetnumber is NOT NULL OR address.housenum is NOT NULL OR "
                     "address.locality is NOT NULL OR address.city is NOT NULL OR address.state is NOT NULL")
            db_info = self.DB.get_table_entry(query, info, address=True)
        elif self.name == 'identity':
            query = ("SELECT identity.clientid, clients.firstname, clients.lastname, identity.pan, portalpass "
                     "FROM clients LEFT JOIN identity ON "
                     "(clients.clientid=address.clientid AND clients.clientid=identity.clientid AND "
                     "(clients.clientid = %(clientid)s OR clients.firstname = %(firstname)s OR "
                     "clients.lastname = %(lastname)s OR clients.pan = %(pan)s)) WHERE "
                     "identity.pan IS NOT NULL OR identity.portalpass IS NOT NULL")
            db_info = self.DB.get_table_entry(query, info, identity=True)
        else:
            print("Table {} is not present in DB {}".format(self.name, self.DBname))
        return db_info

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

    def _compare_info(self, info: dict, dbinfo: dict):
        """compare given information with information obtained from db and see what the difference is"""

        name_check = False
        id_check = False
        pan_check = False
        add_check = True
        # clients table only
        if info['firstname'] == dbinfo['firstname'] and info['lastname'] == dbinfo['lastname']:
            name_check = True
        if info['clientid'] == dbinfo['clientid']:
            id_check = True
        if info['pan'] == dbinfo['pan']:
            pan_check = True
        # if self.name == 'clients':
        # identity table only
        # if self.name == 'identity':
        #     if info['pan'] == dbinfo['pan']:
        #         pan_check = True
        # address table only
        if self.name == 'address':
            if info['street_name'] != dbinfo['streetname'] or info['street_num'] != dbinfo['streetnumber'] or \
                    str(info['house_num']) != dbinfo['housenum'] or info['locality'] != dbinfo['locality'] or \
                    info['city'] != dbinfo['city'] or info['state'] != dbinfo['state'] or \
                    info['pin'] != dbinfo['pin']:
                add_check = False

        return name_check, id_check, pan_check, add_check

    def check_client(self, data):
        """check if given client in present in clients table to change
        client ID in info to match ID already present in clients"""

        db_info = self._check_table(data)
        info_list = None
        id_check, name_check, pan_check, add_check = False, False, False, True
        if db_info:
            info_list = self._list2dict(db_info)
        if info_list is not None and info_list:
            name_check, id_check, pan_check, add_check = self._compare_info(data, info_list[0])
            info_list = info_list[0]
        else:
            info_list = None
        return id_check, name_check, pan_check, add_check, info_list

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






