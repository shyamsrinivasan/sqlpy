from dbclass import Dbcon


engine_config = {'db_type': 'mysql', 'dbapi': 'mysqldb',
                 'username': 'root', 'password': 'root',
                 'server': 'localhost', 'db_name': 'sqlalchemy'}
obj = Dbcon(engine_config)
engine = obj.register_engine()
session = obj.register_session()

