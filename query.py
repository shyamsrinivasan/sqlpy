import mysql.connector
from mysql.connector import errorcode


def querydb(dbconfig={}, query='', query_args={}, printflag=False):
    """connect to mysql db using connector"""

    flag = False
    if not dbconfig:
        print('Empty database configuration information')
        return flag
    else:
        try:
            cnx = mysql.connector.connect(**dbconfig)
            cursor = cnx.cursor()
            if query_args:
                cursor.execute(query, query_args)   # execute given query in mysql object
            else:
                cursor.execute(query)
            if printflag:
                # print statement only good for taxdb.clients
                for (first_name, last_name, client_id) in cursor:
                    print("{} {} is a client with ID: {}".format(first_name, last_name, client_id))
            cursor.close()
            cnx.close()

            flag = True

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            cnx.close()

    return flag


def add2db(dbconfig, add_query, add_data):
    """add data to tables in existing db"""

    flag = False
    try:
        cnx = mysql.connector.connect(**dbconfig)
        cursor = cnx.cursor()
        cursor.execute(add_query, add_data)  # execute given query in mysql object
        cnx.commit()    # commit changes to db
        cursor.close()
        cnx.close()
        flag = True

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cnx.close()

    return flag



