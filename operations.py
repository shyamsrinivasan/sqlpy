import pandas as pd
import sqlalchemy.orm

import table as tb
# from dbclass import Dbcon
# import reflect as rf
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine, inspect
from sqlalchemy import text, desc, and_


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
    def reflect_table(engine):
        """# reflect table from DB given a create_engine instance
        and map to given ORM classes"""
        # engine = ops_obj.register_engine()
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

    def add_data(self, session, data_list=None, file_name=None):
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
        old_last_id = self._get_last_id(session, table_name='customer')
        new_user = self._enter_data(session, data_list=data_list, table_name='customer')

        # match names and add customer_id to data_list
        data_list = self._add_user_id_to_list(pd.DataFrame(data_list), new_user)

        # new_name = {'first': 'Harry', 'last': 'Ried'}
        # user_id = self._get_any_id(session, 'customer', new_name)
        # add data to tax_info table
        new_user = self._enter_data(session, data_list=data_list, table_name='tax_info')

        return old_last_id, new_user

    @staticmethod
    def _get_last_id(session: sqlalchemy.orm.sessionmaker, table_name: str):
        """return last id in customer table"""
        last_id_fun = _last_id_factory(table_name)
        return last_id_fun(session)

    @staticmethod
    def _get_any_id(session_obj: sqlalchemy.orm.sessionmaker, category: str, name: dict):
        id_fun = _get_id_factory(category)
        return id_fun(session_obj, name)

    @staticmethod
    def _add_user_id_to_list(df_of_names: pd.DataFrame, db_user_id: list):
        """add user id from db to given list of names"""

        # add column id to df
        n_rows = df_of_names.shape[0]
        df_of_names = df_of_names.assign(user_id=pd.Series([0] * n_rows))   #, index=df_of_names.index)
        for j_user in db_user_id:
            df_of_names.loc[df_of_names['firstname'] == j_user['firstname'], 'user_id'] = j_user['user_id'][0]
        data_list = df_of_names.to_dict('records')
        return data_list

    def _enter_customer_data(self, data_list: list, session_obj: sqlalchemy.orm.sessionmaker):
        """create Customer object and add object to mapped table as row"""
        old_last_id = self._get_last_id(session_obj, table_name='customer')
        # session_maker_obj = db_obj.register_session()
        with session_obj.begin() as session:
            user_obj_list = [tb.Customer(firstname=j_row['firstname'],
                                         lastname=j_row['lastname'],
                                         email=j_row['email'],
                                         phone=j_row['phone'])
                             for j_row in data_list]
            session.add_all(user_obj_list)

            n_records = len(user_obj_list)
            # name, firstname, lastname = [], [], []
            added_user = [{'firstname': j_row.firstname,
                           'lastname': j_row.lastname}
                          for j_row in user_obj_list]
            # name.append([])
            pass

        # get ids for inserted names and return all added customer names and ids
        for _, i_name in enumerate(added_user):
            new_name = {'first': i_name['firstname'],
                        'last': i_name['lastname']}
            user_id = self._get_any_id(session_obj, 'customer', new_name)
            i_name['user_id'] = user_id

        # get all added ids
            # for j_row in user_obj_list:
            #     # add row object to session
            #     # session.add(j_row)
            #     # collect names of added records
            #     name.append(j_row['name'])
            #     firstname.append(j_row['firstname'])
            #     lastname.append(j_row['lastname'])

        # last_id = self._get_last_id(session_obj, table_name='customer')
        return added_user

    def _enter_tax_data(self, data_list: list, session_obj: sqlalchemy.orm.sessionmaker):
        """create TaxInfo object and add object as row to mapped table"""

        # create tax info object and insert into tax info table
        with session_obj.begin() as session:
            tax_obj = [tb.TaxInfo(user_id=j_user['user_id'],
                                  pan=j_user['pan'])
                       for j_user in data_list]

        # INSERT INTO tax_info(user_id, pan) SELECT user_id, 'pan' FROM customer
        # WHERE firstname='first' AND lastname='last' LIMIT 1
        return None

    def _enter_transactions(self, data_list, db_obj):
        return None

    def _data_entry_factory(self, table_name: str, data_list: list,
                            session_obj: sqlalchemy.orm.sessionmaker):
        """factory function to enter data to different tables in db"""
        if table_name == 'customer':
            return self._enter_customer_data(data_list, session_obj)
        elif table_name == 'tax_info':
            return self._enter_tax_data(data_list, session_obj)
        elif table_name == 'transactions':
            return None
            # return self._enter_transactions(data_list, session_obj)
        else:
            raise ValueError(table_name)

    def _enter_data(self, session_obj: sqlalchemy.orm.sessionmaker,
                    data_list=None, table_name=None):
        """enter data in file_name to customer table"""
        # old_last_id = self._get_last_id(db_obj, table_name)
        if data_list is not None:
            # entry_func = self._data_entry_factory(table_name, data_list, db_obj)
            # new_last_id = entry_func(data_list, db_obj)
            return self._data_entry_factory(table_name, data_list, session_obj)

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
            #     # for row in results:
            #     #     last_id.append(row.id)
            #     #     firstname.append(row.firstname)

            # return old_last_id, new_last_id
        else:
            print('File name to enter data is empty')
            return None

    # def drop_table(self, table_nam):

    def read_data(self):
        """read rows from table after reflecting table using ORM"""
        self.reflect_table()
        with self.Session.begin() as session:
            # session.query
            # rf.Customer
            print("table reflected")
        # with Session(self.engine) as session:


def _last_id_factory(table_name: str):
    if table_name == 'customer':
        return _get_last_customer_id
    elif table_name == 'tax_info':
        return _get_last_tax_info_id
    elif table_name == 'transactions':
        return _get_last_transaction_id
    else:
        raise ValueError(table_name)


def _get_last_customer_id(session_obj: sqlalchemy.orm.sessionmaker):
    """return last id in customer table"""
    last_id = None
    # session_maker_obj = db_obj.register_session()
    with session_obj.begin() as session:
        last_user = session.query(tb.Customer).order_by(desc(tb.Customer.id)).first()
        last_id = last_user.id
    return last_id


def _get_last_tax_info_id(session_obj: sqlalchemy.orm.sessionmaker):
    """return last id in tax info table"""
    last_id = None
    # session_maker_obj = db_obj.register_session()
    with session_obj.begin() as session:
        last_tax_info = session.query(tb.TaxInfo).order_by(desc(tb.TaxInfo.id)).first()
        last_id = last_tax_info.id
    return last_id


def _get_last_transaction_id(session_obj: sqlalchemy.orm.sessionmaker):
    """return last id in transactions table"""
    last_id = None
    # session_maker_obj = db_obj.register_session()
    with session_obj.begin() as session:
        last_transaction = \
            session.query(tb.Transactions).order_by(desc(tb.Transactions.id)).first()
        last_id = last_transaction.id
    return last_id


def _get_id_factory(category: str):
    """return fun for relevant id"""
    if category == 'customer':
        return _get_customer_id
    elif category == 'tax':
        return None
    elif category == 'transaction':
        return None
    else:
        raise ValueError(category)


def _get_customer_id(session_obj: sqlalchemy.orm.sessionmaker, name: dict):
    """return user id for given customer"""
    user_id = []
    # session_maker_obj = db_obj.register_session()
    with session_obj.begin() as session:
        user_obj_id = session.query(tb.Customer.id).\
            where(and_(tb.Customer.firstname == name['first'],
                       tb.Customer.lastname == name['last']))
        user_id = [row.id for row in user_obj_id]
    return user_id
