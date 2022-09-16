from operations import Operations
import os.path
from db_config import engine, session


if __name__ == '__main__':
    ops_obj = Operations()

    # drop all tables
    # ops_obj.drop_table(engine)
    # create all tables in db
    # ops_obj.create_table(engine)

    # reflect table from DB given a Dbcon instance
    ops_obj.reflect_table(engine)

    # add data from file/dictionary
    file_name = os.path.join(os.getcwd(), 'sampleinfo.xlsx')
    customers = ops_obj.add_data(session, file_name=file_name)

    # delete data from db
    flag = ops_obj.delete_data(session, table_name='tax_info', column='customer_id',
                               condition_type='=', condition=2)
    flag = ops_obj.delete_data(session, table_name='address', column='customer_id',
                               condition_type='=', condition=2)
    flag = ops_obj.delete_data(session, table_name='customer', column='id',
                               condition_type='=', condition=2)
    flag = ops_obj.delete_data(session, table_name='customer', column='id',
                               condition_type='>', condition=3)

    # if table_names (db not empty)
    # then proceed with operations
    # with ops_obj.Session.begin() as session:
    #     print("In session")
        # session.inspect.has_table

    ops_obj.read_data()


