import pytest

from app.backend import process_query
from app.backend.sqlite_interface import SqliteController


class TestQueryProcessing:
    def test_find_cols_col_name_col_match(self):
        clause = "col0, col1, col2"
        all_cols = ["col1", "col2", "col6"]
        assert process_query.find_cols(clause, all_cols) == ["col1", "col2"]

    def test_find_cols_col_none_found(self):
        clause = "col4, col5, col6"
        all_cols = ["col1", "col2", "col3"]
        assert process_query.find_cols(clause, all_cols) == []

    def test_find_cols_col_name_substring_collision(self):
        clause = "col0, col12, col2"
        all_cols = ["col1", "col2", "col6"]
        assert process_query.find_cols(clause, all_cols) == ["col2"]

    def test_sel_where_intersection_sel_superset(self):
        sel_cols = ["col0", "col2", "col3"]
        where_cols = ["col0", "col2"]
        assert process_query.cols_added_to_sel(sel_cols, where_cols) == []

    def test_sel_where_intersection_sel_subset(self):
        sel_cols = ["col0", "col2", "col3"]
        where_cols = ["col0", "col2", "col4", "col5"]
        assert set(process_query.cols_added_to_sel(sel_cols, where_cols)) == {"col4", "col5"}

    def test_find_query_clauses_lowered(self):
        query = "select col5, col6 from table where col5=42"
        assert process_query.find_query_clauses(query) == (
            "col5, col6",
            "table",
            "col5=42"
        )

    def test_find_query_clauses_upper(self):
        query = "SELECT Col5, Col6 FROM table where COL5=42"
        assert process_query.find_query_clauses(query) == (
            "Col5, Col6",
            "table",
            "COL5=42"
        )

    def test_find_query_clauses_no_where(self):
        query = "SELECT Col5, Col6 FROM table"
        assert process_query.find_query_clauses(query) == (
            "Col5, Col6",
            "table",
            ""
        )

    def test_difficulty_check_group_by(self):
        with pytest.raises(process_query.DifficultyNotImplemented):
            process_query.difficulty_check_query("SELECT col1, col2 FROM table WHERE col1=2 GROUP BY col2")
        with pytest.raises(process_query.DifficultyNotImplemented):
            process_query.difficulty_check_query("SELECT col1, col2 FROM table WHERE col1=2 group by col2")

    def test_difficulty_check_aggregation(self):
        with pytest.raises(process_query.DifficultyNotImplemented):
            process_query.difficulty_check_query("SELECT COUNT(col1), col2 FROM table WHERE col1=2")
        with pytest.raises(process_query.DifficultyNotImplemented):
            process_query.difficulty_check_query("SELECT min(col1), col2 FROM table WHERE col1=2")

    def test_difficulty_check_nested(self):
        with pytest.raises(process_query.DifficultyNotImplemented):
            process_query.difficulty_check_query("SELECT col1, col2 FROM table WHERE col1=in (SELECT col1 FROM table)")
        with pytest.raises(process_query.DifficultyNotImplemented):
            process_query.difficulty_check_query("SELECT col1, col2 FROM table WHERE col1=in (select col1 FROM table)")

    def test_difficulty_check_expected(self):
        assert process_query.difficulty_check_query(
            "SELECT col1, col2 FROM table WHERE col1=5")


@pytest.fixture(autouse=True, scope='class')
def get_db_interface():
    db_test_path = "resources/test_tables.db"
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
