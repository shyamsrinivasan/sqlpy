from sqlalchemy import create_engine
from sqlalchemy.orm import Session


if __name__ == '__main__':
    engine = create_engine('mysql+mysqldb://root:root@localhost/taxdata')
    with Session(engine) as session:
        result = session.execute()
        session.commit()
