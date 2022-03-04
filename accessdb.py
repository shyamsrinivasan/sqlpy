import mysql.connector
from mysql.connector import errorcode


def getinfo(sqlobj, tables=False, columns=False, id_only=False, client=False, address=False, identity=False,
            all_details=False):
    """get entries from db using given query. Fetch all relevant details from all tables in db"""

    result = None
    if all_details:
        id_only, client, address, identity = True, True, True, True
    try:
        cnx = mysql.connector.connect(**sqlobj.dbconfig)
        cursor = cnx.cursor(dictionary=True)
        if sqlobj.query_args is None:
            cursor.execute(sqlobj.query)
        else:
            cursor.execute(sqlobj.query, sqlobj.query_args)  # execute given query in mysql object
        client_id, last_name, first_name, pan = [], [], [], []
        str_num, str_name, house_num, locale, city, state, pin = [], [], [], [], [], [], []
        portal_pass = []
        table_names, column_names, column_dtype, column_default, is_null = [], [], [], [], []
        for row in cursor:
            if tables:
                table_names.append(row['TABLE_NAME'])
            if columns:
                column_names.append(row['COLUMN_NAME'])
                column_dtype.append(row['DATA_TYPE'])
                column_default.append(row['COLUMN_DEFAULT'])
                is_null.append(row['IS_NULLABLE'])
            if id_only:
                client_id.append(row['clientid'])
            if client or address or identity:
                client_id.append(row['clientid'])
                first_name.append(row['firstname'])
                last_name.append(row['lastname'])
                pan.append(row['pan'])
            if address:
                str_name.append(row['streetname'])
                str_num.append(row['streetnumber'])
                house_num.append(row['housenum'])
                locale.append(row['locality'])
                city.append(row['city'])
                state.append(row['state'])
                pin.append(row['pin'])
            if identity:
                portal_pass.append(row['portalpass'])
        if tables or columns:
            result = {'table_names': table_names, 'column_names': column_names, 'column_dtype': column_dtype,
                      'is_null': is_null, 'default': column_default}
        if client or address or identity:
            result = {'firstname': first_name, 'lastname': last_name, 'clientid': client_id, 'pan': pan,
                      'streetnumber': str_num, 'streetname': str_name, 'housenum': house_num, 'locality': locale,
                      'city': city, 'state': state, 'pin': pin, 'portalpass': portal_pass}
        if id_only:
            result = {'id': client_id}
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        cnx.rollback()
    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()
    return result


def query_db(sqlobj):
    """connect to mysql db using connector and query, add to or
    update db using relevant queries passed as input"""

    flag = False
    if sqlobj.dbconfig is None:
        print('Empty database configuration information')
        return flag
    else:
        try:
            cnx = mysql.connector.connect(**sqlobj.dbconfig)
            cursor = cnx.cursor()
            if sqlobj.query_args is None:
                cursor.execute(sqlobj.query)
            else:
                cursor.execute(sqlobj.query, sqlobj.query_args)  # execute given query in mysql object
            cnx.commit()
            flag = True

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("SQL Error: Username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("SQL Error: Database does not exist")
            elif err.errno == errorcode.ER_KEY_COLUMN_DOES_NOT_EXITS:
                print('SQL Error: Column specified in query does not exist')
            elif err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print('SQL Error: Table with name to be added already exists in DB')
            else:
                print(err)
            cnx.rollback()
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()
    return flag
