from sqlalchemy import create_engine
from tables import create_table
from reflect import reflect_table
from sqlalchemy.orm import Session
from operations import Operations


def execute_session(engine, create=False, reflect=False):
    """execute a sql process with/without session object"""
    if create:
        create_table(engine)

    if reflect:
        reflect_table(engine)


if __name__ == '__main__':
    # create_engine('db_type+dbapi://username:password@localhost/db_name')
    engine = create_engine('mysql+mysqldb://root:root@localhost/sqlalchemy')
    execute_session(engine, reflect=True)
    # with Session(engine) as session:
    #     result = session.execute()
    #     session.commit()
    engine_config = {'db_type': 'mysql', 'dbapi': 'mysqldb',
                     'username': 'root', 'password': 'root',
                     'server': 'localhost', 'db_name': 'sqlalchemy'}
    ops_obj = Operations(engine_config)
