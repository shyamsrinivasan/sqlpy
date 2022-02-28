import pandas
import pandas as pd


class PySQL:
    def __init__(self, dbconfig):
        self.DBname = dbconfig['database']
        # SQL connection properties in dictionary
        self.dbconfig = dbconfig
        # query and query arguments (change for different query calls)
        self.query = ''
        self.query_args = None
        self.query_flag = None
        # get info on all tables (table name, column names) in db
        self.tables = []
        # self._get_tables()

    def _get_tables(self):
        """get all tables associated with DB using MySQl connector"""

        # get DB table info
        self.query = ("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE "
                      "TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = %(db_name)s")
        self.query_args = {'db_name': self.DBname}
        table_info = getinfo(self, tables=True)

        # create PySQltable objects for each table and create list of table objects
        if table_info['table_names']:
            for i_table in table_info['table_names']:
                i_table_info = {'database': self.DBname, 'table_name': i_table}
                table_obj = PySQLtable(self, i_table_info)
                self.tables.append(table_obj)


class PySQLtable:
    def __init__(self, db_obj, init):
        self.DBname = init['database']
        self.name = init['table_name']
        # get info on all columns in table
        self.column_names = None
        self.column_dtype = None
        self.is_null = None
        self.column_default = None
        self.columns = 0
        self._get_columns(db_obj)
        if init.get('key') is not None:
            self.keys = init['key']
        else:
            self.keys = None
        if init.get('foreign_key') is not None:
            self.foreign_key = init['foreign_key']
        else:
            self.foreign_key = None

    def _get_columns(self, db_obj):
        """get all column names for listed tables in DB"""

        # get column names, column type, column nullablity and column default
        db_obj.query = ("SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, COLUMN_DEFAULT, IS_NULLABLE, COLUMN_KEY "
                        "FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = %(table_name)s")
        db_obj.query_args = {'table_name': self.name}
        column_info = getinfo(db_obj, columns=True)
        self.column_names = column_info['column_names']
        self.column_dtype = column_info['column_dtype']
        self.is_null = column_info['is_null']
        self.column_default = column_info['default']
        self.columns = len(self.column_names)