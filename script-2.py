from dbclass import Dbcon
from operations import Operations


def get_object(engine_config):
    obj = Dbcon(engine_config)
    return obj


if __name__ == '__main__':
    engine_config = {'db_type': 'mysql', 'dbapi': 'mysqldb',
                     'username': 'root', 'password': 'root',
                     'server': 'localhost', 'db_name': 'sqlalchemy'}
    obj = get_object(engine_config)
    ops_obj = Operations()

    ops_obj.reflect_table(ops_obj.engine)

    # add data from file/dictionary
    file_name = os.path.join(os.getcwd(), 'sampleinfo.xlsx')
    # with ops_obj.Session.begin() as session:
    customer_obj = ops_obj.add_data(file_name=file_name)