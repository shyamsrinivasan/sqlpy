from dbclass import Dbcon
from operations import Operations
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
    ops_obj.drop_table(engine)
    # create all tables in db
    ops_obj.create_table(engine)

    # reflect table from DB given a Dbcon instance
    ops_obj.reflect_table(engine)

    # add data from file/dictionary
    file_name = os.path.join(os.getcwd(), 'sampleinfo.xlsx')
    users, tax_info = ops_obj.add_data(session, file_name=file_name)

    # delete data from db
    flag_2 = ops_obj.delete_data(session, table_name='tax_info', column='user_id',
                                 condition_type='=', condition=2)