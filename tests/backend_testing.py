import pytest

from app.backend import process_query


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
