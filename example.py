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

    # create PySQL db object
    db = PySQL(dbconfig)
    # read data from Excel file and write to mysql db
    file_name = os.path.join(os.getcwd(), 'sampleinfo.xlsx')
    db = db.enter_data(file_name)

    # add new column to DB and relevant data
    # type_column = {'name': 'client_type', 'dtype': 'VARCHAR(15)', 'is_null': 'NOT NULL',
    #                'default': 'personal'}   # 'other': 'AUTO_INCREMENT'
    from_date = {'name': 'from_date', 'dtype': 'TIMESTAMP', 'is_null': 'NOT NULL', 'default': 'CURRENT_TIMESTAMP'}
    to_date = {'name': 'to_date', 'dtype': 'TIMESTAMP'}
    column_property = [from_date, to_date]
    db = db.add_column(table_name='address', col_prop=column_property)

    # drop columns from db tables
    db = db.drop_column(table_name='address', column_name=['last_update'])

    # additional queries to print results for
    query = "SELECT firstname, lastname, clientid, pan FROM clients"
    db.print_query_info(query, client=True)

    # display all databases in the current SQL server
    # showdb_query = "SHOW DATABASES"
    # cursor.execute(showdb_query)
    # for db in cursor:
    #     print(db)







