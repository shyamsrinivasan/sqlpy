# from sqlalchemy import inspect
# from tables import create_table
# from reflect import reflect_table
# from sqlalchemy.orm import sessionmaker
from operations import Operations
from dbclass import Dbcon
from table import Reflected
import os.path


def get_object(engine_config):
    """return engine and session objects"""
    obj = Dbcon(engine_config)
    engine_obj = obj.register_engine()
    session_obj = obj.register_session()
    return session_obj, engine_obj


if __name__ == '__main__':
    engine_config = {'db_type': 'mysql', 'dbapi': 'mysqldb',
                     'username': 'root', 'password': 'root',
                     'server': 'localhost', 'db_name': 'sqlalchemy'}
    session, engine = get_object(engine_config)
    ops_obj = Operations()

    # drop all tables
    # ops_obj.drop_table(engine)
    # create all tables in db
    # ops_obj.create_table(engine)

    # reflect table from DB given a Dbcon instance
    ops_obj.reflect_table(engine)

    # execute_session(engine, reflect=True)
    # with Session(engine) as session:
    #     result = session.execute()
    #     session.commit()

    # add data from file/dictionary
    file_name = os.path.join(os.getcwd(), 'sampleinfo.xlsx')
    # customer_obj = ops_obj.add_data(session, file_name=file_name)

    # delete data from db
    flag_2 = ops_obj.delete_data(session, table_name='tax_info', column='user_id',
                                 condition_type='>', condition=2)
    flag = ops_obj.delete_data(session, table_name='customer', column='id',
                               condition_type='>', condition=2)

    # if table_names (db not empty)
    # then proceed with operations
    # with ops_obj.Session.begin() as session:
    #     print("In session")
        # session.inspect.has_table

    # reflect and select data
    # meta_obj = MetaData(engine)
    # meta_obj.reflect()
    # my_table = meta_obj.tables['my_table_name']
    ops_obj.read_data()


