# from sqlalchemy import inspect
# from tables import create_table
# from reflect import reflect_table
# from sqlalchemy.orm import sessionmaker
from operations import Operations
from table import Reflected
import os.path


if __name__ == '__main__':
    engine_config = {'db_type': 'mysql', 'dbapi': 'mysqldb',
                     'username': 'root', 'password': 'root',
                     'server': 'localhost', 'db_name': 'sqlalchemy'}
    ops_obj = Operations(engine_config)
    # execute_session(engine, reflect=True)
    # with Session(engine) as session:
    #     result = session.execute()
    #     session.commit()

    # reflect table from DB given a create_engine instance
    ops_obj.reflect_table()

    # add data from file/dictionary
    file_name = os.path.join(os.getcwd(), 'sampleinfo.xlsx')
    ops_obj.enter_data(file_name=file_name)

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


