from typing import List

import pandas as pd
import pymysql
import sshtunnel
import yaml
from sshtunnel import SSHTunnelForwarder

from app.backend.db.DbInterface import DbInterface


class MySqlController(DbInterface):
    def __init__(self, credentials_path: str):
        with open(credentials_path, 'r') as stream:
            self.credentials = yaml.safe_load(stream)

        # Since the db is not hosted in localhost we first have to connect through ssh
        # with the host machine and then execute the queries using the ssh tunnel.
        self.tunnel = self._open_ssh_tunnel()
        # self.connection = self._mysql_connect()

    def _open_ssh_tunnel(self) -> SSHTunnelForwarder:
        """Open an SSH tunnel and connect using a username and password."""
        # tunnel = SSHTunnelForwarder(
        #     (self.credentials['MYSQL']['SSH_HOST'],
        #      self.credentials['MYSQL']['SSH_PORT']),
        #     ssh_username=self.credentials['MYSQL']['SSH_USERNAME'],
        #     ssh_password=self.credentials['MYSQL']['SSH_PASSWORD'],
        #     remote_bind_address=(self.credentials['MYSQL']['DATABASE_HOST'],
        #                          self.credentials['MYSQL']['DATABASE_PORT']),
        #     local_bind_address=(self.credentials['MYSQL']['DATABASE_HOST'],
        #                         self.credentials['MYSQL']['DATABASE_PORT'])
        #
        # )


        with sshtunnel.open_tunnel(
                ("darelab.imsi.athenarc.gr", 15000),
                ssh_username="mxydas",
                ssh_password='D9kD$JD$qY1K',
                remote_bind_address=("127.0.0.1", 3306),
                local_bind_address=("127.0.0.1", 8892)
        ) as tunnel:
            conn = pymysql.connect(host='127.0.0.1', user=self.credentials['MYSQL']['DATABASE_USERNAME'],
                                   passwd=self.credentials['MYSQL']['DATABASE_PASSWORD'],
                                   db=self.credentials['MYSQL']['DATABASE_NAME'],
                                   port=8892)
            query = '''SELECT VERSION();'''
            data = pd.read_sql_query(query, conn)
            print(data)
            conn.close()

        # tunnel.start()
        # print("Done")
        # return tunnel

    def _mysql_connect(self) -> pymysql.Connection:
        """Connect to a MySQL server using the SSH tunnel connection"""
        connection = pymysql.connect(
            host=self.credentials['MYSQL']['DATABASE_HOST'],
            user=self.credentials['MYSQL']['DATABASE_USERNAME'],
            passwd=self.credentials['MYSQL']['DATABASE_PASSWORD'],
            # database="cordis"
            db=self.credentials['MYSQL']['DATABASE_NAME'],
            port=8899
        )

        return connection

    def shutdown(self) -> None:
        """ Close the mysql connection and the tunnel"""
        self.connection.close()
        self.tunnel.close()

    def query_with_res_cols(self, query: str):
        return pd.read_sql_query(query, self.connection)

    def get_table_names(self) -> List[str]:
        return []

    def get_table_cols(self, table_name: str) -> List[str]:
        return []

    def preview_table(self, table: str, limit: int = 10):
        return []


if __name__ == '__main__':
    mysql_controller = MySqlController("../config/credentials.yaml")
    print(mysql_controller.query_with_res_cols("SELECT * FROM projects LIMIT 10"))
