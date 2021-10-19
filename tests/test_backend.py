import pytest
from mo_sql_parsing import parse

from app.backend.db.SqliteController import SqliteController
from app.backend.processing import process_query


class TestQueryProcessing:
    def test_transform_query_same_sel_where(self):
        assert process_query.transform_query("SELECT col1 FROM table_name WHERE col1=2") == \
               ("SELECT col1 FROM table_name WHERE col1 = 2 LIMIT 1", "table_name")

    def test_transform_query_diff_sel_where(self):
        assert process_query.transform_query("SELECT col1 FROM table_name WHERE col2=2") == \
               ("SELECT col1, col2 FROM table_name WHERE col2 = 2 LIMIT 1", "table_name")

    def test_transform_query_diff_sel_star(self):
        assert process_query.transform_query("SELECT * FROM table_name WHERE col2=2") == \
               ("SELECT * FROM table_name WHERE col2 = 2 LIMIT 1", "table_name")

    def test_add_limit_1_limit_1_exists(self):
        assert process_query.add_limit_1({'select': [{'value': 'col_name'}], 'from': 'table_name', "limit": 1}) == \
               {'select': [{'value': 'col_name'}], 'from': 'table_name', "limit": 1}

    def test_add_limit_1_limit_not_exists(self):
        assert process_query.add_limit_1({'select': [{'value': 'col_name'}], 'from': 'table_name'}) == \
               {'select': [{'value': 'col_name'}], 'from': 'table_name', "limit": 1}

    def test_add_limit_1_limit_else_exists(self):
        assert process_query.add_limit_1({'select': [{'value': 'col_name'}], 'from': 'table_name', "limit": 5}) == \
               {'select': [{'value': 'col_name'}], 'from': 'table_name', "limit": 1}

    def test_aggr_exists_dict(self):
        assert process_query.check_aggr_exists([{'value': {'count': 'bbb'}}])
        assert process_query.check_aggr_exists([{'value': {'max': 'bbb'}}])
        assert process_query.check_aggr_exists([{'value': {'min': 'bbb'}}])
        assert process_query.check_aggr_exists([{'value': {'avg': 'bbb'}}])
        assert process_query.check_aggr_exists([{'value': {'sum': 'bbb'}}])

    def test_aggr_exists_list(self):
        assert process_query.check_aggr_exists([{'value': 'dd'}, {'value': {'count': 'bbb'}}])
        assert process_query.check_aggr_exists([{'value': {'max': 'ccc'}}, {'value': 'dd'},
                                                {'value': {'count': 'bbb'}}])

    def test_aggr_not_exists_list(self):
        assert process_query.check_aggr_exists([{'value': 'dd'}]) is False
        assert process_query.check_aggr_exists([{'value': 'dd'}, {'value': 'cc'}, {'value': 'country'}]) is False

    def test_aggr_not_exists_star(self):
        assert process_query.check_aggr_exists(["*"]) is False

    def test_find_where_cols_simple(self):
        assert process_query.find_where_cols({'eq': ['aa', 15]}) == {'aa'}

    def test_find_where_cols_complex(self):
        assert process_query.find_where_cols({'or': [{'and': [{'eq': ['aa', 15]}, {'eq': ['bb', 12]}]},
                                                     {'gt': ['cc', 13]}]}) \
               == {'aa', 'bb', 'cc'}

    def test_find_sel_cols_list(self):
        assert process_query.find_sel_cols([{'value': 'dd'}]) == {'dd'}
        assert process_query.find_sel_cols([{'value': 'jobs.cc'}, {'value': 'dd'}]) == {'jobs.cc', 'dd'}

    def test_find_sel_cols_str(self):
        assert process_query.find_sel_cols(['*']) == {'*'}

    def test_difficulty_check_group_by(self):
        with pytest.raises(process_query.DifficultyNotImplemented):
            process_query.difficulty_check_query(parse("SELECT col1, col2 FROM table WHERE col1=2 GROUP BY col2"))
        with pytest.raises(process_query.DifficultyNotImplemented):
            process_query.difficulty_check_query(parse("SELECT col1, col2 FROM table WHERE col1=2 group by col2"))

    def test_difficulty_check_aggregation(self):
        with pytest.raises(process_query.DifficultyNotImplemented):
            process_query.difficulty_check_query(parse("SELECT COUNT(col1), col2 FROM table WHERE col1=2"))
        with pytest.raises(process_query.DifficultyNotImplemented):
            process_query.difficulty_check_query(parse("SELECT min(col1), col2 FROM table WHERE col1=2"))

    def test_difficulty_check_nested(self):
        with pytest.raises(process_query.DifficultyNotImplemented):
            process_query.difficulty_check_query(
                parse("SELECT col1, col2 FROM table WHERE col1=in (SELECT col1 FROM table)"))
        with pytest.raises(process_query.DifficultyNotImplemented):
            process_query.difficulty_check_query(
                parse("SELECT col1, col2 FROM table WHERE col1=in (select col1 FROM table)"))

    def test_difficulty_check_expected(self):
        assert process_query.difficulty_check_query(
            parse("SELECT col1, col2 FROM table WHERE col1=5"))


@pytest.fixture(autouse=True, scope='class')
def get_db_interface():
    db_test_path = "tests/resources/test_tables.db"
    return SqliteController(db_test_path)


class TestSqliteInterface:
    def test_get_tables_no_sqlite_master(self, get_db_interface):
        assert "sqlite_master" not in get_db_interface.get_table_names()

    def test_get_tables_titanic_included(self, get_db_interface):
        assert "titanic" in get_db_interface.get_table_names()

    def test_number_of_returned(self, get_db_interface):
        assert len(get_db_interface.get_table_names()) == 1

    def test_get_table_cols_expected_length(self, get_db_interface):
        assert len(get_db_interface.get_table_cols('titanic')) == 7

    def test_get_table_cols_expected_values(self, get_db_interface):
        assert get_db_interface.get_table_cols('titanic') \
               == ["PassengerId", "Survived", "Name", "Sex", "Age",
                   "Ticket", "Fare"]

    def test_preview_table_rows_len(self, get_db_interface):
        assert len(get_db_interface.preview_table('titanic')['row']) == 10

    def test_preview_table_rows_values(self, get_db_interface):
        rows_cols = get_db_interface.preview_table('titanic')
        first_row = rows_cols['row'][0]
        cols = rows_cols['header']
        assert cols == ["PassengerId", "Survived", "Name", "Sex", "Age", "Ticket", "Fare"]
        assert first_row == (1, 'Survived', 'Karina Davis', 'male', 22, 'A/5 21171', 7.25)
