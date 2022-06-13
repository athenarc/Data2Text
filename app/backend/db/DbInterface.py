from abc import ABC, abstractmethod
from typing import List


class DbInterface(ABC):
    """
    Contains the methods that should be implemented from any interface. Currently, MySQL and sqlite are implemented
    but this interface could be expanded to other relational and non-relational DBs.
    """
    @abstractmethod
    async def query_with_res_cols(self, conn_url: str, query: str):
        """ Executes the query and along with the results (rows) it also returns the names of the columns. """

    @abstractmethod
    async def get_table_names(self, conn_url: str) -> List[str]:
        """ Returns the table names of the database we have connected to. """

    @abstractmethod
    async def get_table_cols(self, conn_url: str, table_name: str) -> List[str]:
        """ Returns the column names of the given table_name. """

    @abstractmethod
    async def get_pks_of_table(self, conn_url: str, table_name: str) -> List[str]:
        """ Returns a list of the primary keys of the given table. """

    @abstractmethod
    async def preview_table(self, conn_url: str, table: str, limit: int = 10):
        """ Returns the first `limit` rows of the given `table` """


class DbException(Exception):
    pass
