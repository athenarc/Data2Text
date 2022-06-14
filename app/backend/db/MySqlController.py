from contextlib import contextmanager
from typing import Dict, List

import pandas as pd
import pandas.io.sql
import pymysql
import sshtunnel
import yaml
from sshtunnel import SSHTunnelForwarder

from app.backend.db.DbInterface import DbException, DbInterface


class MySqlController(DbInterface):
    # def __init__(self, credentials_path: str):
    #     with open(credentials_path, 'r') as stream:
    #         self.credentials = yaml.safe_load(stream)

    def query_with_res_cols(self, query: str):
        try:
            with get_connection(**self._mysql_connection_args()) as con:
                res = pd.read_sql_query(query, con)
        except pandas.io.sql.DatabaseError as e:
            raise DbException(f"ERROR: {e}")
        return list(res.itertuples(index=False, name=None)), list(res.columns)

    def get_table_names(self) -> List[str]:
        table_query = f"""
        SELECT table_name
        FROM INFORMATION_SCHEMA.TABLES
        WHERE table_schema = \'{self.credentials['MYSQL']['DATABASE_NAME']}\';
        """

        with get_connection(**self._mysql_connection_args()) as con:
            table_names = pd.read_sql_query(table_query, con)
        return list(table_names.TABLE_NAME)

    def get_table_cols(self, table_name: str) -> List[str]:
        table_cols_query = f"""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = \'{self.credentials['MYSQL']['DATABASE_NAME']}\' AND TABLE_NAME = \'{table_name}\';
        """
        with get_connection(**self._mysql_connection_args()) as con:
            table_cols = pd.read_sql_query(table_cols_query, con)
        return list(table_cols.COLUMN_NAME)

    def get_pks_of_table(self, table_name: str) -> List[str]:
        pks_of_table_query = f"""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{self.credentials['MYSQL']['DATABASE_NAME']}'
          AND TABLE_NAME = '{table_name}'
          AND COLUMN_KEY = 'PRI';
        """
        with get_connection(**self._mysql_connection_args()) as con:
            table_pks = pd.read_sql_query(pks_of_table_query, con)
        return list(table_pks.COLUMN_NAME)

    def preview_table(self, table: str, limit: int = 10):
        rows, cols = self.query_with_res_cols(f"SELECT * FROM {table} LIMIT {limit}")
        return {"table": table, "header": cols, "row": rows}


if __name__ == '__main__':
    mysql_controller = MySqlController("../config/credentials.yaml")
    # res_rows, desc = mysql_controller.query_with_res_cols("SELECT * FROM projects LIMIT 10")
    # print(res_rows)
    # print(desc)
    #
    # print(mysql_controller.get_table_names())
    # print(mysql_controller.get_table_cols("projects"))
    # print(mysql_controller.preview_table("projects"))
    print(mysql_controller.get_pks_of_table('projects'))
