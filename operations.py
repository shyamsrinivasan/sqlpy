import pandas as pd


class Operations:
    """Contains methods for different operations on python classes"""

    def __init__(self, engine_config):
        self._engine_call = engine_config['db_type'] + \
                            '+' + \
                            engine_config['dbapi'] + \
                            '://' + \
                            engine_config['username'] + \
                            ':' + \
                            engine_config['password'] + \
                            '@' + \
                            engine_config['server'] + \
                            '/' + \
                            engine_config['db_name']

    @staticmethod
    def _read_from_file(file_name=None):
        """read client info from file to dataframe"""

        if file_name is not None:
            # read excel file with client data into pandas
            df = pd.read_excel(file_name, 'info', engine='openpyxl')
        else:
            df = None

        # fill nan values (for non NaN columns in db) with appropriate replacement
        if df is not None:
            df['phone'].fillna('none', inplace=True)
            df['email'].fillna('none', inplace=True)
            df['aadhaar'].fillna('none', inplace=True)
            df['type'].fillna('personal', inplace=True)
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

    def enter_data(self, file_name=None, table_name=None):
        """enter data in file_name to all tables in table_name"""

        if file_name is not None:
            data = self._read_from_file(file_name)
            # add client ID to new data
            # data = self._assign_id(data, id_col='clientid')
            if table_name is not None:
                # add data only to selected tables
                print('Adding data to given tables only')
            else:
                # add data to all tables in db one table at a time
                # add data to parent table (clients) first
                # tab_obj = [j_table for j_table in self.tables if j_table.name == 'clients'][0]
                # print("Adding data to table {} in current DB {}".format(tab_obj.name, self.DBname))
                # # check if data present in clients table. Change client id if present
                # data_list = data.to_dict('records')  # convert data df to list of dict
                # for i_data in data_list:
                #     id_check, name_check, pan_check, add_check, info_list = tab_obj.check_client(i_data)
                #     if info_list is not None and info_list:
                #         if (name_check or pan_check) and not id_check:
                #             i_data['clientid'] = info_list['clientid']
                # tab_obj.add_data(data_list)
                # # add data to other (child) tables
                # for j_table in self.tables:
                #     if j_table.name != 'clients':
                #         print("Adding data to table {} in current DB {}".format(j_table.name, self.DBname))
                #         j_table.add_data(data_list)
                #     else:
                #         continue
                pass
        else:
            print('File name to enter data is empty')
        return self
