import pandas as pd
import table as tb
# import reflect as rf
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, inspect
from sqlalchemy import text, desc


class Operations:
    """Contains methods for different operations on python classes"""

    def __init__(self):  #, engine_config):
        # self.table_names = self._get_table_names()

        self.empty_db = True
        # if self.table_names:
        #     self.empty_db = False

        # if not self.empty_db:
        #     self._reflect_table()

    @staticmethod
    def reflect_table(ops_obj):
        """# reflect table from DB given a create_engine instance
        and map to given ORM classes"""
        engine = ops_obj.register_engine()
        tb.Reflected.prepare(engine)

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

    def add_data(self, db_obj, data_list=None, file_name=None):
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
        customer_objs = self._enter_data(db_obj, data_list=data_list, table_name='customer')
        # get customer_id for added data
        # add data to tax_info table
        return customer_objs

    @staticmethod
    def _get_last_id(db_obj):
        """return last id in customer table"""
        last_id = None
        session_maker_obj = db_obj.register_session()
        with session_maker_obj.begin() as session:
            last_user = session.query(tb.Customer).order_by(desc(tb.Customer.id)).first()
            last_id = last_user.id
        return last_id

    def _enter_customer_data(self, data_list, db_obj):
        user_obj_list = [tb.Customer(firstname=j_row['firstname'],
                                     lastname=j_row['lastname'])
                         for j_row in data_list]
        session_maker_obj = db_obj.register_session()
        with session_maker_obj.begin() as session:
            session.add_all(user_obj_list)
            # for j_row in user_obj_list:
            #     session.add(j_row)

    def _enter_data(self, db_obj, data_list=None, table_name=None):
        """enter data in file_name to customer table"""
        if data_list is not None:
            if table_name == 'customer':
                self._enter_customer_data(data_list, db_obj)
                # user_obj_list = [tb.Customer(firstname=j_row['firstname'],
                #                              lastname=j_row['lastname'])
                #                  for j_row in data_list]
                # session_maker_obj = db_obj.register_session()
                # with session_maker_obj.begin() as session:
                #     session.add_all(user_obj_list)
                    # for j_row in user_obj_list:
                    #     session.add(j_row)

                # get user_id from customer table for
                last_id = self._get_last_id(db_obj)
                # firstname = []
                # last_id = []
                # with session_maker_obj.begin() as session:
                #     cust_obj = tb.Customer()
                #     column = cust_obj.get_column(column_name='firstname')
                #     query = session.query(tb.Customer).filter(column == 'Harry')
                #     engine_obj = db_obj.register_engine()
                #     data = pd.read_sql_query(query.statement, engine_obj)
                #     # results = session.query(tb.Customer).all()
                #     # results = session.query(tb.Customer).from_statement(text("SELECT LAST (id) FROM customer"))
                #     last_user = session.query(tb.Customer).order_by(desc(tb.Customer.id)).first()
                #     last_id = last_user.id
                #     # for row in results:
                #     #     last_id.append(row.id)
                #     #     firstname.append(row.firstname)

                return last_id

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

    # def drop_table(self, table_nam):

    def read_data(self):
        """read rows from table after reflecting table using ORM"""
        self.reflect_table()
        with self.Session.begin() as session:
            # session.query
            # rf.Customer
            print("table reflected")
        # with Session(self.engine) as session:

