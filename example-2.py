from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


# create connection engine - Connect object for Core
engine = create_engine('mysql+mysqldb://root:root@localhost/taxdata')
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM taxdata.clients"))
    print(result.all())

# Session object for ORM
statement = text("SELECT * FROM taxdata.clients")
with Session(engine) as session:
    result = session.execute(statement)
    # session.commit()
    for row in result:
        print(f"name: {row.firstname} ID:{row.clientid}")



