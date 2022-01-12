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



