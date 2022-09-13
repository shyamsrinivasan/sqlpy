import unittest
from operations import Operations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestOperations(unittest.TestCase):

    def test_create_table(self):
        ops_obj = Operations()
        _engine_call = 'mysql+mysqldb://root:root@localhost/sqlalchemy'
        engine = create_engine(_engine_call, echo=True)
        ops_obj.create_table(engine)
        # self.assertTrue(any_class_method_returning_boolean)
        pass

    def test_drop_table(self):
        ops_obj = Operations()
        _engine_call = 'mysql+mysqldb://root:root@localhost/sqlalchemy'
        engine = create_engine(_engine_call, echo=True)
        ops_obj.drop_table(engine)
        # self.assertTrue(any_class_method_returning_boolean)
        pass

    def test_add_data(self):
        pass

    def test_delete_data(self):
        pass


if __name__ == '__main__':
    unittest.main()