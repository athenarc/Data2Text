# import pytest
#
# from app.backend.db.SqliteController import SqliteController
#
#
# @pytest.fixture(autouse=True, scope='class')
# def get_db_interface():
#     return SqliteController()
#
#
# DATABASE_CONN = "sqlite://///home/mikexydas/PycharmProjects/Data2Text/tests/resources/test_tables.db"
#
#
# class TestSqliteInterface:
#     def test_get_tables_no_sqlite_master(self, get_db_interface):
#         assert "sqlite_master" not in get_db_interface.get_table_names(DATABASE_CONN)
#
#     def test_get_tables_titanic_included(self, get_db_interface):
#         assert "titanic" in get_db_interface.get_table_names(DATABASE_CONN)
#
#     def test_number_of_returned(self, get_db_interface):
#         assert len(get_db_interface.get_table_names(DATABASE_CONN)) == 1
#
#     def test_get_table_cols_expected_length(self, get_db_interface):
#         assert len(get_db_interface.get_table_cols('titanic')) == 7
#
#     def test_get_table_cols_expected_values(self, get_db_interface):
#         assert get_db_interface.get_table_cols('titanic') \
#                == ["PassengerId", "Survived", "Name", "Sex", "Age",
#                    "Ticket", "Fare"]
#
#     def test_preview_table_rows_len(self, get_db_interface):
#         assert len(get_db_interface.preview_table('titanic')['row']) == 10
#
#     def test_preview_table_rows_values(self, get_db_interface):
#         rows_cols = get_db_interface.preview_table('titanic')
#         first_row = rows_cols['row'][0]
#         cols = rows_cols['header']
#         assert cols == ["PassengerId", "Survived", "Name", "Sex", "Age", "Ticket", "Fare"]
#         assert first_row == (1, 'Survived', 'Karina Davis', 'male', 22, 'A/5 21171', 7.25)
