from abc import ABC, abstractmethod
from typing import List


class DbInterface(ABC):
    """
    Contains the methods that should be implemented from any interface. Currently, MySQL and sqlite are implemented
    but this interface could be expanded to other relational and non-relational DBs.
    """
    @abstractmethod
    def query_with_res_cols(self, query: str):
        """ Executes the query and along with the results (rows) it also returns the names of the columns. """

    @abstractmethod
    def get_table_names(self) -> List[str]:
        """ Returns the table names of the database we have connected to. """

    @abstractmethod
    def get_table_cols(self, table_name: str) -> List[str]:
        """ Returns the column names of the given table_name. """

    @abstractmethod
    def preview_table(self, table: str, limit: int = 10):
        """ Returns the first `limit` rows of the given `table` """

    @abstractmethod
    def shutdown(self) -> None:
        """ Do any cleanup if necessary. Eg. close the connection."""
