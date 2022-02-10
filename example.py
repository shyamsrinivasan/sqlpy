from query import querydb
from load import loadclientinfo
import pandas as pd
import os.path


def readclientinfo() -> object:
    """read client info from file to dataframe"""

    # write_flag = False
    # read excel file with client data into pandas
    df = pd.read_excel(os.path.join(os.getcwd(), 'sampleinfo.xlsx'), 'info', engine='openpyxl')

    # fill nan values (for non NN columns in db) with appropriate replacement
    df['house_num'].fillna('0A', inplace=True)
    df['locality'].fillna('none', inplace=True)

    # get first and last names from full name
    firstname = [iname.split()[0] for iname in df['name']]
    lastname = [iname.split()[1] for iname in df['name']]
    df = df.assign(firstname=pd.Series(firstname))
    df = df.assign(lastname=pd.Series(lastname))
    return df


if __name__ == '__main__':
    """script to test mySQL python connector"""
    # step 1 - connect to sql db/query db for values
    dbconfig = {'user': 'root',
                'password': 'root',
                'host': '127.0.0.1',
                'database': 'taxdata',
                'raise_on_warnings': True}

    """script to test reading data fgrom excel file and writing to mysql db"""
    data = readclientinfo()
    loadclientinfo(data, dbconfig)

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







