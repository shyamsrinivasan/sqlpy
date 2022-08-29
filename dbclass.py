from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker


class Dbcon:
    def __init__(self, engine_config):
        # self._engine_call = ''
        self._engine_call = engine_config['db_type'] + \
                            '+' + \
                            engine_config['dbapi'] + \
                            '://' + \
                            engine_config['username'] + \
                            ':' + \
                            engine_config['password'] + \
                            '@' + \
                            engine_config['server'] + \
                            '/' + \
                            engine_config['db_name']
        # create_engine('db_type+dbapi://username:password@localhost/db_name')
        # self.engine = ''
        # self.engine = create_engine(self._engine_call, echo=True)
        # self.Session = sessionmaker(self.engine)
        # self.inspect = inspect(self.engine)

    def register_engine(self):
        return create_engine(self._engine_call, echo=True)

    def register_session(self):
        engine = self.register_engine()
        return sessionmaker(engine)

    def _register_inspector(self):
        engine = self.register_engine()
        return inspect(engine)

    def check_table(self, table_name=None):
        """check if given table exists in db"""
        inspect_obj = self._register_inspector()
        if inspect_obj.has_table(table_name=table_name):
            return True
        return False

    def get_table_names(self):
        """get all table names in reflected db"""
        inspect_obj = self._register_inspector()
        return inspect_obj.get_table_names()
