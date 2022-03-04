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

        # fill nan values (for non NaN columns in db) with appropriate replacement
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
        return self

    def change_table_entry(self, query, query_args=None):
        """call query_db to add/update entry in table"""

        self.query = query
        self.query_args = query_args
        self._reset_query_flag()
        self.query_flag = query_db(self)
        return self

    def get_table_entry(self, query, query_args=None, id_only=False, client=False, address=False, identity=False,
                        all_details=False):
        """call get_info to get entry from db using SELECT"""

        self.query = query
        self.query_args = query_args
        self._reset_query_flag()
        dbinfo = getinfo(self, id_only=id_only, client=client, address=address, identity=identity,
                         all_details=all_details)
        return dbinfo

    def print_query_info(self, query, query_args=None, id_only=False, client=False, address=False, identity=False,
                            all_details=False):

        db_info = self.get_table_entry(query, query_args=query_args, id_only=id_only, client=client, address=address,
                                       identity=identity, all_details=all_details)

        # print statement only good for taxdb.clients
        if client:
            if db_info is not None and db_info:
                nres = len([val for val in db_info['firstname'] if db_info['firstname']])
            else:
                nres = 0
            for ival in range(0, nres):
                print("{} {} is a client with ID: {}".format(db_info['firstname'][ival], db_info['lastname'][ival],
                                                             db_info['clientid'][ival]))

    def add_column(self, table_name, col_prop):
        """add column to given table and ensure they have col_property"""

        if table_name is not None:
            tab_obj = [j_table for j_table in self.tables if j_table.name == table_name]
            if tab_obj:
                # add data only to selected table
                tab_obj = tab_obj[0]
                print("Adding column to table {} in current DB {}".format(tab_obj.name, self.DBname))
                tab_obj.add_column(col_prop)
            else:
                print('Error in given table name {}. No such table in DB {}'.format(table_name, self.DBname))
        else:
            print('Table name to add column is empty')


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

        update_data = [False] * len(data)
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
                    # update entry only in other tables
                    print("Client {} {} is present in DB with ID:{} and PAN:{}. "
                          "Existing entry can only be updated".format(i_entry['firstname'], i_entry['lastname'],
                                                                      info_list['clientid'],
                                                                      info_list['pan']))
                    update_data[idx] = True
                else:
                    if name_check and not pan_check:
                        print("Client {} {} is present in DB with different PAN:{}".format(i_entry['firstname'],
                                                                                           i_entry['lastname'],
                                                                                           info_list['pan']))
                        if info_list['pan']:
                            i_entry['pan'] = info_list['pan']
                        # may be update PAN in clients and identity?
                        # if info_list['pan']:
                        #     i_entry['pan'] = info_list['pan']
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
                    # update address
                    self._update_entry(info_list, i_entry)
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
            if entry_info['house_num'] == 'none':
                query = ("INSERT INTO {}.{} "
                         "(clientid, streetnumber, streetname, housenum, locality, city, state, pin) "
                         "VALUES (%(clientid)s, %(street_num)s, %(street_name)s, NULL, %(locality)s, %(city)s, "
                         "%(state)s, %(pin)s)".format(self.DBname, self.name))
            else:
                query = ("INSERT INTO {}.{} "
                         "(clientid, streetnumber, streetname, housenum, locality, city, state, pin) "
                         "VALUES (%(clientid)s, %(street_num)s, %(street_name)s, %(house_num)s, %(locality)s, "
                         "%(city)s, %(state)s, %(pin)s)".format(self.DBname, self.name))
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
            query = ("SELECT address.clientid, clients.firstname, clients.lastname, clients.pan, streetnumber, "
                     "streetname, housenum, locality, city, state, pin "
                     "FROM clients LEFT JOIN address ON (clients.clientid=address.clientid AND "
                     "(clients.clientid = %(clientid)s OR clients.firstname = %(firstname)s OR "
                     "clients.lastname = %(lastname)s OR clients.pan = %(pan)s)) WHERE address.streetname is NOT NULL "
                     "OR address.streetnumber is NOT NULL OR address.housenum is NOT NULL OR "
                     "address.locality is NOT NULL OR address.city is NOT NULL OR address.state is NOT NULL")
            db_info = self.DB.get_table_entry(query, info, address=True)
        elif self.name == 'identity':
            query = ("SELECT identity.clientid, clients.firstname, clients.lastname, identity.pan, portalpass "
                     "FROM clients LEFT JOIN identity ON "
                     "(clients.clientid=identity.clientid AND clients.clientid=identity.clientid AND "
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
            if info_list[0]['housenum'] is None:
                info_list[0]['housenum'] = 'none'
            name_check, id_check, pan_check, add_check = self._compare_info(data, info_list[0])
            info_list = info_list[0]
        else:
            info_list = None
        return id_check, name_check, pan_check, add_check, info_list

    def _update_entry(self, dbinfo: dict, data: dict):
        """update a single/single type of entry in db"""

        if self.name == 'client':
            # update pan or other details
            if data['clientid'] != dbinfo['clientid']:
                # same name but different client id -> change to same client id
                query = ("UPDATE {}.{} SET clientid = %(clientid)s WHERE clients.firstname = %(firstname)s "
                         "AND clients.lastname = %(lastname)s".format(self.DBname, self.name))
                self.DB = self.DB.change_table_entry(query, data)
                if self.DB.query_flag:
                    print("Client ID changed ID from {} to {} for `{} {}`  has ".format(dbinfo['clientid'],
                                                                                        data['clientid'],
                                                                                        dbinfo['firstname'],
                                                                                        dbinfo['lastname']))
                else:
                    print('NO CHANGE in client ID made for `{} {}`. Old client ID: {}'.format(dbinfo['firstname'],
                                                                                              dbinfo['lastname'],
                                                                                              dbinfo['clientid']))

            if data['firstname'] != dbinfo['firstname']:
                query = ("UPDATE {}.{} SET firstname = %(firstname)s "
                         "WHERE clients.clientid = %(clientid)s".format(self.DBname, self.name))
                self.DB = self.DB.change_table_entry(query, data)
                if self.DB.query_flag:
                    print("First name changed to `{}` for client:{} `{} {}`".format(data['firstname'],
                                                                                    dbinfo['clientid'],
                                                                                    dbinfo['firstname'],
                                                                                    dbinfo['lastname']))
                else:
                    print("First name NOT CHANGED to `{}` for "
                          "client:{} `{} {}`".format(data['firstname'], dbinfo['clientid'],
                                                     dbinfo['firstname'], dbinfo['lastname']))

            if data['lastname'] != dbinfo['lastname']:
                query = ("UPDATE {}.{} SET lastname = %(lastname)s "
                         "WHERE clients.clientid = %(clientid)s".format(self.DBname, self.name))
                self.DB = self.DB.change_table_entry(query, data)
                if self.DB.query_flag:
                    print("Last name changed to `{}` for client: {} `{} {}`".format(data['lastname'],
                                                                                    dbinfo['clientid'],
                                                                                    dbinfo['firstname'],
                                                                                    dbinfo['lastname']))
                else:
                    print("Last name NOT CHANGED to `{}` for "
                          "client: {} `{} {}`".format(data['lastname'], dbinfo['clientid'],
                                                      dbinfo['firstname'], dbinfo['lastname']))

            if data['pan'] != dbinfo['pan']:
                print('PAN cannot be changed')

        elif self.name == 'address':
            # update address details
            if data['street_num'] != dbinfo['streetnumber']:
                query = ("UPDATE {}.{} SET streetnumber = %(street_num)s "
                         "WHERE address.clientid = %(clientid)s".format(self.DBname, self.name))
                self.DB = self.DB.change_table_entry(query, data)
                if self.DB.query_flag:
                    print("Street number changed from {} to {} for `{} {}`".format(dbinfo['streetnumber'],
                                                                                   data['street_num'],
                                                                                   dbinfo['firstname'],
                                                                                   dbinfo['lastname']))
                else:
                    print("Street number NOT CHANGED from {} to {} for "
                          "`{} {}`".format(dbinfo['streetnumber'], data['street_num'], dbinfo['firstname'],
                                           dbinfo['lastname']))
            if data['street_name'] != dbinfo['streetname']:
                query = ("UPDATE {}.{} SET streetname = %(street_name)s "
                         "WHERE address.clientid = %(clientid)s".format(self.DBname, self.name))
                self.DB = self.DB.change_table_entry(query, data)
                if self.DB.query_flag:
                    print("Street name changed from {} to {} for `{} {}`".format(dbinfo['streetname'],
                                                                                 data['street_name'],
                                                                                 dbinfo['firstname'],
                                                                                 dbinfo['lastname']))
                else:
                    print("Street name NOT CHANGED from {} to {} for "
                          "`{} {}`".format(dbinfo['streetname'], data['street_name'], dbinfo['firstname'],
                                           dbinfo['lastname']))
            # house number can be empty
            if data['house_num'] != dbinfo['housenum']:
                if data['house_num'] == 'none':
                    query = ("UPDATE {}.{} SET housenum = NULL "
                             "WHERE address.clientid = %(clientid)s".format(self.DBname, self.name))
                else:
                    query = ("UPDATE {}.{} SET housenum = %(house_num)s "
                             "WHERE address.clientid = %(clientid)s".format(self.DBname, self.name))
                self.DB = self.DB.change_table_entry(query, data)
                if self.DB.query_flag:
                    print("House number changed from {} to {} for `{} {}`".format(dbinfo['housenum'],
                                                                                  data['house_num'],
                                                                                  dbinfo['firstname'],
                                                                                  dbinfo['lastname']))
                else:
                    print("House number NOT CHANGED from {} to {} for `{} {}`".format(dbinfo['housenum'],
                                                                                      data['house_num'],
                                                                                      dbinfo['firstname'],
                                                                                      dbinfo['lastname']))
            # locality can be empty
            if data['locality'] != dbinfo['locality']:
                if data['locality'] == 'none':
                    query = ("UPDATE {}.{} SET locality = NULL "
                             "WHERE address.clientid = %(clientid)s".format(self.DBname, self.name))
                else:
                    query = ("UPDATE {}.{} SET locality = %(locality)s "
                             "WHERE address.clientid = %(clientid)s".format(self.DBname, self.name))
                self.DB = self.DB.change_table_entry(query, data)
                if self.DB.query_flag:
                    print("Locality changed from {} to {} for `{} {}`".format(dbinfo['locality'], data['locality'],
                                                                              dbinfo['firstname'], dbinfo['lastname']))
                else:
                    print("Locality NOT CHANGED from {} to {} for `{} {}`".format(dbinfo['locality'], data['locality'],
                                                                                  dbinfo['firstname'],
                                                                                  dbinfo['lastname']))

            if data['city'] != dbinfo['city']:
                query = ("UPDATE {}.{} SET city = %(city)s "
                         "WHERE address.clientid = %(clientid)s".format(self.DBname, self.name))
                self.DB = self.DB.change_table_entry(query, data)
                if self.DB.query_flag:
                    print("City changed from {} to {} for `{} {}`".format(dbinfo['city'], data['city'],
                                                                          dbinfo['firstname'], dbinfo['lastname']))
                else:
                    print("City NOT CHANGED from {} to {} for `{} {}`".format(dbinfo['city'], data['city'],
                                                                              dbinfo['firstname'],
                                                                              dbinfo['lastname']))
            if data['state'] != dbinfo['state']:
                query = ("UPDATE {}.{} SET state = %(state)s "
                         "WHERE address.clientid = %(clientid)s".format(self.DBname, self.name))
                self.DB = self.DB.change_table_entry(query, data)
                if self.DB.query_flag:
                    print("State changed from {} to {} for `{} {}`".format(dbinfo['state'], data['state'],
                                                                           dbinfo['firstname'], dbinfo['lastname']))
                else:
                    print("State NOT CHANGED from {} to {} for `{} {}`".format(dbinfo['state'], data['state'],
                                                                               dbinfo['firstname'],
                                                                               dbinfo['lastname']))
            if data['pin'] != dbinfo['pin']:
                query = ("UPDATE {}.{} SET pin = %(pin)s "
                         "WHERE address.clientid = %(clientid)s".format(self.DBname, self.name))
                self.DB = self.DB.change_table_entry(query, data)
                if self.DB.query_flag:
                    print("PIN changed from {} to {} for `{} {}`".format(dbinfo['pin'], data['pin'],
                                                                         dbinfo['firstname'], dbinfo['lastname']))
                else:
                    print("PIN NOT CHANGED from {} to {} for `{} {}`".format(dbinfo['pin'], data['pin'],
                                                                             dbinfo['firstname'],
                                                                             dbinfo['lastname']))

        elif self.name == 'identity':
            # update pan or other identity details
            if data['portalpass'] != dbinfo['portalpass']:
                query = ("UPDATE {}.{} SET portalpass = %(portalpass)s "
                         "WHERE clients.clientid = %(clientid)s".format(self.DBname, self.name))
                self.DB = self.DB.change_table_entry(query, data)
                if self.DB.query_flag:
                    print("Portal password changed to {} for `{} {}`".format(data['portalpass'], dbinfo['firstname'],
                                                                             dbinfo['lastname']))
                else:
                    print("Portal password NOT CHANGED for `{} {}`".format(dbinfo['firstname'], dbinfo['lastname']))
        else:
            print('Update commands not available for {} in {}'.format(self.name, self.DBname))

    def add_column(self, col_prop):
        """add column in table (self.name) using properties provided in col_prop"""

        ncols = len(col_prop)
        for idx, i_col in enumerate(col_prop):
            # check if column is present in table
            if i_col['name'] in self.column_names:
                print('Column name matches column already present in table. '
                      'Provide different column name for {} or remove existing column'.format(i_col['name']))
                continue
            else:
                print('Adding column {} of {}'.format(idx, ncols))
                # create PySQLNewColumn object for each new column to be added
                col = PySQLNewColumn(i_col)
                col = col.build_query(self.name)
                self.DB = self.DB.change_table_entry(col.query, col.query_args)
                if self.DB.query_flag:
                    print('Column {} added to {}'.format(col.name, self.name))
                else:
                    print('Column {} NOT added to {}'.format(col.name, self.name))


class PySQLNewColumn:
    def __init__(self, init):
        if init.get('name') is not None:
            self.name = init['name']
        else:
            self.name = None
        if init.get('dtype') is not None:
            self.dtype = init['dtype']
        else:
            self.dtype = 'VARCHAR(50)'
        if init.get('is_null') is not None:
            self.is_null = init['is_null']
        else:
            self.is_null = None
        if init.get('default') is not None and init['default']:
            self.default = init['default']
        else:
            self.default = None
        if init.get('other') is not None and init['other']:
            self.other = init['other']
        else:
            self.other = None

        self.query = None
        self.query_args = None

    def build_query(self, table_name):
        """build query statement required to add column object to any table"""

        # query = ("ALTER TABLE {} alter_option".format())
        # ALTER TABLE table_name ADD column_name column_dtype column_is_null column_default/other_value
        # ALTER TABLE t2 ADD c INT UNSIGNED NOT NULL AUTO_INCREMENT
        start = "ALTER TABLE {} ".format(table_name)

        # add column name and column dtype (default is VARCHAR(50) if not given)
        start += "ADD {} {}".format(self.name, self.dtype)

        # NULL or NOT NULL
        if self.is_null is not None:
            start += " {}".format(self.is_null)

        if self.default is not None:
            start += " DEFAULT %(default)s"
            query_args = {'default': self.default}
        elif self.other is not None:
            start += " {}".format(self.other)

        self.query = start
        self.query_args = query_args
        return self
