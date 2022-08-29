import pandas as pd
import table as tb
# import reflect as rf
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, inspect


# class Dbcon:
#     def __init__(self, engine_config):
#         # self._engine_call = ''
#         self._engine_call = engine_config['db_type'] + \
#                             '+' + \
#                             engine_config['dbapi'] + \
#                             '://' + \
#                             engine_config['username'] + \
#                             ':' + \
#                             engine_config['password'] + \
#                             '@' + \
#                             engine_config['server'] + \
#                             '/' + \
#                             engine_config['db_name']
#         # create_engine('db_type+dbapi://username:password@localhost/db_name')
#         # self.engine = ''
#         # self.engine = create_engine(self._engine_call, echo=True)
#         # self.Session = sessionmaker(self.engine)
#         # self.inspect = inspect(self.engine)
#
#     def _register_engine(self):
#         return create_engine(self._engine_call, echo=True)
#
#     def register_session(self):
#         engine = self._register_engine()
#         return sessionmaker(engine)
#
#     def register_inspector(self):
#         engine = self._register_engine()
#         return inspect(engine)


class Operations:
    """Contains methods for different operations on python classes"""

    def __init__(self):  #, engine_config):
        # self._engine_call = engine_config['db_type'] + \
        #                     '+' + \
        #                     engine_config['dbapi'] + \
        #                     '://' + \
        #                     engine_config['username'] + \
        #                     ':' + \
        #                     engine_config['password'] + \
        #                     '@' + \
        #                     engine_config['server'] + \
        #                     '/' + \
        #                     engine_config['db_name']
        # create_engine('db_type+dbapi://username:password@localhost/db_name')
        # self.engine = create_engine(self._engine_call, echo=True)
        # self.Session = sessionmaker(self.engine)
        # self.inspect = inspect(self.engine)
        # self.table_names = self._get_table_names()

        self.empty_db = True
        # if self.table_names:
        #     self.empty_db = False

        # if not self.empty_db:
        #     self._reflect_table()

    # @staticmethod
    # def check_table(ops_obj, table_name=None):
    #     """check if given table exists in db"""
    #     inspect_obj = ops_obj.register_inspector()
    #     if inspect_obj.has_table(table_name=table_name):
    #         return True
    #     return False

    # @staticmethod
    # def get_table_names(ops_obj):
    #     """get all table names in reflected db"""
    #     inspect_obj = ops_obj.register_inspector()
    #     return inspect_obj.get_table_names()

    @staticmethod
    def reflect_table(ops_obj):
        """# reflect table from DB given a create_engine instance
        and map to given ORM classes"""
        engine = ops_obj.register_engine()
        tb.Reflected.prepare(engine)

    # def add_table(self, table_class_orm):
    #     """add table defined as a class using ORM Base.create_all"""

    # def drop_table(self, table_nam):

    # def execute_session(self, create=False, reflect=False):
    #     """execute a sql process with/without session object"""
    #     if create:
    #         tb.create_table(engine=self._engine)

        # if reflect:
        #     rf.reflect_table(self.engine)

    # def add_row(engine, row):
    #     """add data to table in db"""
    #     with Session(engine) as session:
    #         session.add(row)

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

    def add_data(self, data_list=None, file_name=None):
        """enter data in file_name to all tables in table_name"""

        # get info from file
        if data_list is None and file_name is None:
            raise ValueError("Data should be provided either as "
                             "dictionary (data_list) or as file (file_name). "
                             "Both should not be Empty")

        if data_list is not None:
            pass

        if file_name is not None:
            data = self._read_from_file(file_name)
            data_list = data.to_dict('records')  # convert data df to list of dict

        # add data to customer table
        customer_objs = self._enter_data(data_list=data_list, table_name='customer')
        # get customer_id for added data
        # add data to tax_info table
        return customer_objs

    def _enter_data(self, data_list=None, table_name=None):
        """enter data in file_name to customer table"""
        if data_list is not None:
            if table_name == 'customer':
                user_obj_list = [tb.Customer(firstname=j_row['firstname'],
                                             lastname=j_row['lastname'])
                                 for j_row in data_list]
                with self.Session.begin() as session:
                    for j_row in user_obj_list:
                        session.add(j_row)

                # get user_id from customer table for
                with self.Session.begin() as session:
                    tb.Customer

                return user_obj_list

        #     if table_name == 'tax_info':
        #         pass
        #         return tax_info_obj_list
        #     if table_name == 'transactions':
        #         pass
        #         return trans_obj_list
        #     pass
        else:
            print('File name to enter data is empty')
            obj_list = []
            return obj_list

    def read_data(self):
        """read rows from table after reflecting table using ORM"""
        self.reflect_table()
        with self.Session.begin() as session:
            # session.query
            # rf.Customer
            print("table reflected")
        # with Session(self.engine) as session:

