from query import querydb
from load import readclientinfo, loadclientinfo
import os.path
from sqlclass import PySQL


if __name__ == '__main__':
    """script to test mySQL python connector"""
    # step 1 - connect to sql db/query db for values
    dbconfig = {'user': 'root',
                'password': 'root',
                'host': '127.0.0.1',
                'database': 'taxdata',
                'raise_on_warnings': True}

    db = PySQL(dbconfig)
    # read data from excel file and write to mysql db
    file_name = os.path.join(os.getcwd(), 'sampleinfo.xlsx')
    data = readclientinfo(file_name)
    loadclientinfo(data, dbconfig)
    # db = db.enter_data(file_name, table_name)

    # add new column to DB and relevant data

    # query = "SELECT firstname, lastname FROM taxdata.clients WHERE clientid=%(client_id)s;"
    # detail = {'client_id': 20002}
    query = "SELECT firstname, lastname, clientid FROM clients"
    # query = "SELECT firstname, lastname FROM taxdata.clients WHERE clientid=%(client_id)s;"
    # detail = {'client_id': 20002}
    querydb(dbconfig, query, printflag=True)

    # step 2 - connect to sql db/add values to db
    # insert data into existing db table
    # client_data = {'client_id': 20006, 'first_name': 'Shikamaru', 'last_name': 'Nara', 'pan': 'SDRF2546RT',
    #                'street_num': '1', 'street_name': 'nowhere st', 'house_num': '', 'locality': '',
    #                'city': 'Everywhere',
    #                'state': 'This', 'pin': 600001, 'portalpass': 'xdst45Ds3rf98S'}
    # loadsingleclientinfo(dbconfig, client_data)

    # query to check addition to db
    querydb(dbconfig, query, printflag=True)

    # display all databases in the current SQL server
    # showdb_query = "SHOW DATABASES"
    # cursor.execute(showdb_query)
    # for db in cursor:
    #     print(db)







