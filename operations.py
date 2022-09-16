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

    @staticmethod
    def reflect_table(engine):
        """# reflect table from DB given a create_engine instance
        and map to given ORM classes"""
        # engine = ops_obj.register_engine()
        tb.Reflected.prepare(engine)

    @staticmethod
    def drop_table(engine):
        tb.drop_table(engine)

    @staticmethod
    def create_table(engine):
        tb.create_table(engine)

    @staticmethod
    def _read_from_file(file_name=None):
        """read client info from file to dataframe"""

        if file_name is not None:
            # read Excel file with client data into pandas
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

    def add_data(self, session: sqlalchemy.orm.sessionmaker,
                 data_list=None, file_name=None):
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
        # check if given customer is already present in customer table
        data_list = self._check_existing_records(data_list, session,
                                                 table_name='customer')
        added_user = self._enter_data(session, data_list=data_list,
                                      table_name='customer')

        if added_user is not None:
            data = pd.DataFrame(data_list)
            to_add = data[['name', 'firstname', 'lastname', 'pan',
                           'street_num', 'street_name', 'house_num',
                           'locality', 'city', 'state', 'pin']]
            full = to_add.merge(pd.DataFrame(added_user), on=['name', 'firstname', 'lastname'])
            data_list = full.to_dict('records')

        # match names and add customer_id to data_list
        # data_list = self._add_customer_id_to_list(data, new_user)

        # add data to tax_info table
        data_list = self._check_existing_records(data_list, session,
                                                 table_name='tax_info')
        added_tax_user = self._enter_data(session, data_list=data_list,
                                          table_name='tax_info')
        # add address to address table
        data_list = self._check_existing_records(data_list, session,
                                                 table_name='address')
        added_address = self._enter_data(session, data_list=data_list,
                                         table_name='address')

        # return all added data as single dataframe
        # merge user and tax if added and get one or both outside as df
        if added_user is not None and added_tax_user is not None:
            user = pd.DataFrame(added_user)
            user_tax = user.merge(pd.DataFrame(added_tax_user),
                                  on=['name', 'customer_id'])
        else:
            if added_user is not None:
                user_tax = pd.DataFrame(added_user)
            elif added_tax_user is not None:
                user_tax = pd.DataFrame(added_tax_user)
            else:
                user_tax = None

        if added_address is not None and user_tax is not None:
            added_data = user_tax.merge(pd.DataFrame(added_address),
                                        on=['name', 'customer_id'])
            return added_data
        elif added_address is not None and user_tax is None:
            return pd.DataFrame(added_address)
        elif added_address is None and user_tax is not None:
            return user_tax
        else:
            return None

    def add_transaction(self, session, data_list):
        """separate method to add transactions to table, since they are added separately"""
        added_trans = self._enter_data(session, data_list=data_list, table_name='transactions')
        return added_trans

    def delete_data(self, session_obj: sqlalchemy.orm.sessionmaker,
                    table_name: str, column, condition_type, condition):
        """remove rows from a given table"""
        table_class = _get_class_name(table_name)
        table_class_attr = _get_class_attribute(table_class, attribute_name=column)
        # delete_value = self._remove_row(table_class_attr, condition_type, condition, session_obj)
        delete_value = self._remove_row(table_class, table_class_attr, condition_type,
                                        condition, session_obj)
        return delete_value

    @staticmethod
    def _get_last_id(session: sqlalchemy.orm.sessionmaker, table_name: str):
        """return last id in customer table"""
        last_id_fun = _last_id_factory(table_name)
        return last_id_fun(session)

    @staticmethod
    def _add_customer_id_to_list(df_of_names: pd.DataFrame, db_customer_id: list):
        """add user id from db to given list of names"""

        # add column id to df
        n_rows = df_of_names.shape[0]
        df_of_names = df_of_names.assign(customer_id=pd.Series([0] * n_rows))   #, index=df_of_names.index)
        for j_user in db_customer_id:
            df_of_names.loc[df_of_names['firstname'] == j_user['firstname'], 'customer_id'] = \
                j_user['customer_id'][0]
        data_list = df_of_names.to_dict('records')
        return data_list

    def _enter_customer_data(self, data_list: list, session_obj: sqlalchemy.orm.sessionmaker):
        """create Customer object and add object to mapped table as row"""
        old_last_id = self._get_last_id(session_obj, table_name='customer')
        session_obj.close_all()
        with session_obj.begin() as session:
            user_obj_list = [tb.Customer(fullname=j_row['name'],
                                         firstname=j_row['firstname'],
                                         lastname=j_row['lastname'],
                                         email=j_row['email'],
                                         phone=j_row['phone'],
                                         type=j_row['type']
                                         )
                             for j_row in data_list if 'customer_id' not in j_row]
            # for j_obj in user_obj_list:
            #     session.add(j_obj)
            session.add_all(user_obj_list)
            n_records = len(user_obj_list)
            added_user = [{'firstname': j_row.firstname,
                           'lastname': j_row.lastname,
                           'name': j_row.fullname}
                          for j_row in user_obj_list]
            session.commit()

        # get ids for inserted names and return all added customer names and ids
        if added_user:
            for _, i_name in enumerate(added_user):
                customer_id = _get_any_id(basis='name', category='customer',
                                          condition=i_name, session_obj=session_obj)
                i_name['customer_id'] = customer_id
            # last_id = self._get_last_id(session_obj, table_name='customer')
            return added_user
        else:
            return None

    def _enter_tax_data(self, data_list: list, session_obj: sqlalchemy.orm.sessionmaker):
        """create TaxInfo object and add object as row to mapped table"""
        # create tax info object and insert into tax info table
        old_last_id = self._get_last_id(session_obj, table_name='tax_info')
        with session_obj.begin() as session:
            tax_obj = [tb.TaxInfo(customer_id=j_user['customer_id'],
                                  customer_name=j_user['name'],
                                  pan=j_user['pan'],
                                  aadhaar='456125874123')
                       # aadhaar=j_user['aadhaar'])
                       for j_user in data_list if 'tax_id' not in j_user]
            session.add_all(tax_obj)
            added_user = [{'name': j_row.customer_name,
                           'pan': j_row.pan,
                           'aadhaar': j_row.aadhaar,
                           'customer_id': j_row.customer_id}
                          for j_row in tax_obj]
            session.commit()

        # get ids for inserted names and return all added tax_info names and ids
        for _, i_name in enumerate(added_user):
            tax_id = _get_any_id(basis='customer_id', category='tax_info',
                                 condition=i_name, session_obj=session_obj)
            i_name['tax_id'] = tax_id

        if added_user:
            return added_user
        else:
            return None

    def _enter_address_data(self, data_list: list,
                            session_obj: sqlalchemy.orm.sessionmaker):
        """create address objects and add as rows to address table"""
        old_last_id = self._get_last_id(session_obj, table_name='address')
        with session_obj.begin() as session:
            address_obj = [tb.Address(customer_id=j_user['customer_id'],
                                      customer_name=j_user['name'],
                                      street_num=j_user['street_num'],
                                      street_name=j_user['street_name'],
                                      house_num=j_user['house_num'],
                                      locality=j_user['locality'],
                                      city=j_user['city'],
                                      state=j_user['state'],
                                      pin=j_user['pin'])
                           for j_user in data_list if 'address_id' not in j_user]
            session.add_all(address_obj)
            added_address = [{'name': j_row.customer_name,
                              'customer_id': j_row.customer_id,
                              'street_num': j_row.street_num,
                              'street_name': j_row.street_name,
                              'house_num': j_row.house_num,
                              'locality': j_row.locality,
                              'city': j_row.city,
                              'state': j_row.state,
                              'pin': j_row.pin
                              }
                             for j_row in address_obj]
            session.commit()

        # get ids for inserted names and return all added tax_info names and ids
        for _, i_name in enumerate(added_address):
            address_id = _get_any_id(basis='customer_id', category='address',
                                     condition=i_name, session_obj=session_obj)
            i_name['address_id'] = address_id

        if added_address:
            return added_address
        else:
            return None

    def _enter_transactions(self, data_list: list, session_obj: sqlalchemy.orm.sessionmaker):
        """create Transactions object and add object as row to mapped table"""
        return None

    def _data_entry_factory(self, table_name: str, data_list: list,
                            session_obj: sqlalchemy.orm.sessionmaker):
        """factory function to enter data to different tables in db"""
        if table_name == 'customer':
            return self._enter_customer_data(data_list, session_obj)
        elif table_name == 'tax_info':
            return self._enter_tax_data(data_list, session_obj)
        elif table_name == 'address':
            return self._enter_address_data(data_list, session_obj)
        # elif table_name == 'transactions':
        #     return self._enter_transactions(data_list, session_obj)
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
            # return old_last_id, new_last_id
        else:
            print('File name to enter data is empty')
            return None

    @staticmethod
    def _check_existing_records(addition_list: dict,
                                session_obj: sqlalchemy.orm.sessionmaker,
                                table_name: str):
        """check table for existing records that match new records
        before adding them to the table"""
        # existing_user_fun = _check_records_factory(table_name)
        for i_customer in addition_list:
            i_customer = _check_existing_records_factory(i_customer,
                                                         session_obj,
                                                         table_name)
            # existing_id =
            # existing_user_id = existing_user_fun(i_customer, session_obj)
            # if existing_user_id:
            #     i_customer['customer_id'] = existing_user_id
        return addition_list

    @staticmethod
    def _remove_row(table_class, table_class_attr, condition_type, condition,
                    session_obj: sqlalchemy.orm.sessionmaker):
        delete_fun = _delete_row_factory(table_class_attr)
        return delete_fun(table_class, table_class_attr, condition_type,
                          condition, session_obj)

    @staticmethod
    def read_data():
        """read rows from table after reflecting table using ORM"""
        # self.reflect_table()
        # with self.Session.begin() as session:
        #     # session.query
        #     # rf.Customer
        #     print("table reflected")
        # with Session(self.engine) as session:
        return None


def _last_id_factory(table_name: str):
    if table_name == 'customer':
        return _get_last_customer_id
    elif table_name == 'tax_info':
        return _get_last_tax_info_id
    elif table_name == 'address':
        return _get_last_address_id
    elif table_name == 'transactions':
        return _get_last_transaction_id
    else:
        raise ValueError(table_name)


def _get_last_customer_id(session_obj: sqlalchemy.orm.sessionmaker):
    """return last id in customer table"""
    # session_maker_obj = db_obj.register_session()
    with session_obj.begin() as session:
        last_user = session.query(tb.Customer).order_by(desc(tb.Customer.id)).first()
        if last_user is not None:
            last_id = last_user.id
        else:
            last_id = None
    return last_id


def _get_last_tax_info_id(session_obj: sqlalchemy.orm.sessionmaker):
    """return last id in tax info table"""
    with session_obj.begin() as session:
        last_tax_info = session.query(tb.TaxInfo).order_by(desc(tb.TaxInfo.id)).first()
        if last_tax_info is not None:
            last_id = last_tax_info.id
        else:
            last_id = None
    return last_id


def _get_last_address_id(session_obj: sqlalchemy.orm.sessionmaker):
    """return last id in address table"""
    with session_obj.begin() as session:
        last_address = session.query(tb.Address).order_by(desc(tb.Address.id)).first()
        if last_address is not None:
            last_id = last_address.id
        else:
            last_id = None
    return last_id


def _get_last_transaction_id(session_obj: sqlalchemy.orm.sessionmaker):
    """return last id in transactions table"""
    with session_obj.begin() as session:
        last_transaction = \
            session.query(tb.Transactions).order_by(desc(tb.Transactions.id)).first()
        last_id = last_transaction.id
    return last_id


def _get_any_id(basis: str, category: str, condition: dict,
                session_obj: sqlalchemy.orm.sessionmaker):
    id_fun = _get_id_factory_type(basis, category)
    return id_fun(condition, session_obj)


def _get_id_factory_type(basis: str, category: str):
    """return fun on whose basis id is to be determined"""
    if basis == 'name':
        # return func that gets ids based on name
        return _get_name_id_factory(category)
    elif basis == 'customer_id':
        # return func that gets ids based on customer_id
        return _get_customer_id_factory(category)
    elif basis == 'transaction_id':
        # return func that gets ids based on transaction_id
        return _get_transaction_id_factory(category)
    else:
        raise ValueError(basis)


def _get_name_id_factory(category: str):
    """return fun for relevant id from name"""
    if category == 'customer':
        return _get_customer_id_from_name
    elif category == 'tax_info':
        return _get_tax_id_from_name
    elif category == 'address':
        return _get_address_id_from_name
    elif category == 'transaction':
        return None
    else:
        raise ValueError(category)


def _get_customer_id_factory(category: str):
    """return fun for relevant id from customer_id"""
    if category == 'tax_info':
        return _get_tax_id_from_customer_id
    elif category == 'address':
        return _get_address_id_from_customer_id
    # elif category == 'transactions':
        # return _get_transaction_from_customer_id
        # return None
    else:
        raise ValueError(category)


def _get_transaction_id_from_customer_id():
    return None


def _get_transaction_id_factory(category: str):
    """return fun for relevant id from transaction id"""
    if category == 'transactions':
        # return _get_customer_id_from_transaction_id
        # return _get_tax_id_from_transaction_id
        return None
    else:
        raise ValueError(category)


def _get_customer_id_from_name(condition: dict,
                               session_obj: sqlalchemy.orm.sessionmaker):
    """return user id for given customer"""
    with session_obj.begin() as session:
        # user_obj_id = session.query(tb.Customer.id).\
        #     where(and_(tb.Customer.firstname == condition['firstname'],
        #                tb.Customer.lastname == condition['lastname']))
        # customer_id = [row.id for row in user_obj_id]
        customer_id = session.query(tb.Customer.id).\
            filter(and_(tb.Customer.firstname == condition['firstname'],
                        tb.Customer.lastname == condition['lastname'])).first()
    if customer_id and customer_id is not None and len(customer_id) <= 1:
        customer_id = customer_id[0]
        return customer_id
    else:
        return []


def _get_tax_id_from_customer_id(condition: dict,
                                 session_obj: sqlalchemy.orm.sessionmaker):
    """return id from tax_info, given customer_id from customer"""
    with session_obj.begin() as session:
        tax_obj_id = session.query(tb.TaxInfo.id). \
            where(tb.TaxInfo.customer_id == condition['customer_id'])
        tax_info_id = [row.id for row in tax_obj_id]
    if tax_info_id is not None and len(tax_info_id) <= 1:
        tax_info_id = tax_info_id[0]
        return tax_info_id
    else:
        return []


def _get_tax_id_from_name(condition: dict, session_obj: sqlalchemy.orm.sessionmaker):
    """return id from tax_info, given customer_name from customer"""
    with session_obj.begin() as session:
        tax_obj_id = session.query(tb.TaxInfo.id).\
            where(tb.TaxInfo.customer_name == condition['name'])
        # tax_obj_id = session.query(tb.TaxInfo.id).\
        #     filter_by(customer_name=condition['name']).first()
        tax_info_id = [row.id for row in tax_obj_id]
    if tax_info_id and tax_info_id is not None and len(tax_info_id) <= 1:
        tax_info_id = tax_info_id[0]
        return tax_info_id
    else:
        return []


def _get_address_id_from_name(condition: dict, session_obj: sqlalchemy.orm.sessionmaker):
    """return id from address, given name"""
    with session_obj.begin() as session:
        address_obj_id = session.query(tb.Address.id).\
            where(tb.Address.customer_name == condition['name'])
        address_id = [row.id for row in address_obj_id]
    if address_id and address_id is not None and len(address_id) <= 1:
        address_id = address_id[0]
        return address_id
    else:
        return []


def _get_address_id_from_customer_id(condition: dict, session_obj: sqlalchemy.orm.sessionmaker):
    """return id from address, given customer_id from customer"""
    with session_obj.begin() as session:
        address_obj_id = session.query(tb.Address.id).\
            where(tb.Address.customer_id == condition['customer_id'])
        address_id = [row.id for row in address_obj_id]
    if address_id is not None and len(address_id) <= 1:
        address_id = address_id[0]
        return address_id
    else:
        return []


def _condition_type_factory(condition_type):
    """decide function based on condition type"""
    if condition_type is '>':
        return _remove_greater_than
    elif condition_type is '<':
        return _remove_less_than
    elif condition_type is '=':
        return _remove_equal_to
    else:
        return None


def _remove_greater_than(table, column, condition):
    return table.__table__.delete().where(column > condition)


def _remove_less_than(table, column, condition):
    return table.__table__.delete().where(column < condition)


def _remove_equal_to(table, column, condition):
    return table.__table__.delete().where(column == condition)


def _delete_row_factory(table_class_attr):
    """factory to delete rows in different tables"""
    # return _remove_customer
    if table_class_attr.class_.__tablename__ == 'customer':
        return _remove_customer
    elif table_class_attr.class_.__tablename__ == 'tax_info':
        return _remove_tax_info
    elif table_class_attr.class_.__tablename__ == 'transactions':
        # return _remove_transactions
        return None
    else:
        return None


def _remove_customer(table, column, condition_type, condition, session_obj):
    """remove row from customer table"""
    delete_query_fun = _condition_type_factory(condition_type)
    delete_query = delete_query_fun(table, column, condition)
    with session_obj.begin() as session:
        session.execute(delete_query)
        session.commit()
    return True


def _remove_tax_info(table, column, condition_type, condition, session_obj):
    """remove row from tax_info table"""
    # find tax_info id corresponding to given condition
    # customer_id = {'customer_id': condition}
    # tax_id = _get_any_id(basis='customer_id', category='tax_info',
    #                      condition=customer_id, session_obj=session_obj)
    delete_query_fun = _condition_type_factory(condition_type)
    delete_query = delete_query_fun(table, column, condition)
    with session_obj.begin() as session:
        session.execute(delete_query)
        session.commit()
    return None


def _remove_transactions(table, column, condition_type, condition, session_obj):
    """remove row from transactions table"""
    return None


def _remove_address():
    """remove row from address table"""
    return None


def _check_existing_records_factory(customer_info: dict,
                                    session_obj: sqlalchemy.orm.sessionmaker,
                                    table_name: str):
    """factory for deciding which id is being returned
    by the check records functions"""
    existing_user_fun = _check_records_factory(table_name)
    if table_name == 'customer':
        existing_id = existing_user_fun(customer_info, session_obj)
        if existing_id:
            customer_info['customer_id'] = existing_id
        return customer_info

    elif table_name == 'tax_info':
        existing_id = existing_user_fun(customer_info, session_obj)
        if existing_id:
            customer_info['tax_id'] = existing_id
        return customer_info

    elif table_name == 'address':
        existing_id = existing_user_fun(customer_info, session_obj)
        if existing_id:
            customer_info['address_id'] = existing_id
        return customer_info

    else:
        raise ValueError(table_name)


def _check_records_factory(table_name: str):
    """return fun that checks for existing records in different tables"""
    if table_name == 'customer':
        return _check_customer_records
    elif table_name == 'tax_info':
        return _check_tax_info_records
    elif table_name == 'address':
        return _check_address_records
    else:
        raise ValueError(table_name)


def _check_customer_records(condition, session_obj):
    """check customer table if given record/records are already present"""
    customer_id = _get_any_id(basis='name', category='customer',
                              condition=condition, session_obj=session_obj)
    return customer_id


def _check_tax_info_records(condition, session_obj):
    """check tax_info table if given record/records are already present"""
    tax_id = _get_any_id(basis='name', category='tax_info',
                         condition=condition, session_obj=session_obj)
    return tax_id


def _check_address_records(condition, session_obj):
    """check address table if given record/records are already present"""
    address_id = _get_any_id(basis='name', category='address',
                             condition=condition, session_obj=session_obj)
    return address_id


def _get_class_name(table_name: str):
    if table_name == 'customer':
        return tb.Customer
    elif table_name == 'tax_info':
        return tb.TaxInfo
    elif table_name == 'transactions':
        return tb.Transactions
    elif table_name == 'address':
        return tb.Address
    else:
        raise ValueError(table_name)


def _get_class_attribute(table_class, attribute_name):
    """get class attribute (class.attr) from attribute name"""
    if hasattr(table_class, attribute_name):
        return getattr(table_class, attribute_name)
    else:
        return None
