from sqlalchemy import create_engine
from tables import create_table
from reflect import reflect_table
# from sqlalchemy.orm import Session


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
