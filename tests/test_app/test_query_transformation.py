import csv
from typing import Tuple

import pytest
from mo_sql_parsing import parse

from app.backend.processing.process_query import (difficulty_check,
                                                  query_pipeline)


class TestQueryTransformation:
    def test_transform_query_same_sel_where(self):
        assert query_pipeline.transform_query("SELECT col1 FROM table_name WHERE col1=2") == \
               ("SELECT col1 FROM table_name WHERE col1 = 2 LIMIT 1", "table_name")

    def test_transform_query_diff_sel_where(self):
        assert query_pipeline.transform_query("SELECT col1 FROM table_name WHERE col2=2") == \
               ("SELECT col1, col2 FROM table_name WHERE col2 = 2 LIMIT 1", "table_name")

    def test_transform_query_diff_sel_star(self):
        assert query_pipeline.transform_query("SELECT * FROM table_name WHERE col2=2") == \
               ("SELECT * FROM table_name WHERE col2 = 2 LIMIT 1", "table_name")

    def test_transform_query_with_join(self):
        assert query_pipeline.transform_query("SELECT t1.col3 FROM t1, t2 WHERE t1.col1 = t2.col1 AND t1.col2=2") == \
               ("SELECT t1.col3 AS \"t1 col3\", t1.col2 AS \"t1 col2\" FROM t1, t2 WHERE t1.col1 = t2.col1 "
                "AND t1.col2 = 2 LIMIT 1", "t1, t2")

    def test_aggr_exists_dict(self):
        assert difficulty_check.check_aggr_exists([{'value': {'count': 'bbb'}}])
        assert difficulty_check.check_aggr_exists([{'value': {'max': 'bbb'}}])
        assert difficulty_check.check_aggr_exists([{'value': {'min': 'bbb'}}])
        assert difficulty_check.check_aggr_exists([{'value': {'avg': 'bbb'}}])
        assert difficulty_check.check_aggr_exists([{'value': {'sum': 'bbb'}}])

    def test_aggr_exists_list(self):
        assert difficulty_check.check_aggr_exists([{'value': 'dd'}, {'value': {'count': 'bbb'}}])
        assert difficulty_check.check_aggr_exists([{'value': {'max': 'ccc'}}, {'value': 'dd'},
                                                   {'value': {'count': 'bbb'}}])

    def test_aggr_not_exists_list(self):
        assert difficulty_check.check_aggr_exists([{'value': 'dd'}]) is False
        assert difficulty_check.check_aggr_exists([{'value': 'dd'}, {'value': 'cc'}, {'value': 'country'}]) is False

    def test_aggr_not_exists_star(self):
        assert difficulty_check.check_aggr_exists(["*"]) is False

    def test_difficulty_check_group_by(self):
        with pytest.raises(difficulty_check.DifficultyNotImplemented):
            difficulty_check.difficulty_check_query(parse("SELECT col1, col2 FROM table WHERE col1=2 GROUP BY col2"))
        with pytest.raises(difficulty_check.DifficultyNotImplemented):
            difficulty_check.difficulty_check_query(parse("SELECT col1, col2 FROM table WHERE col1=2 group by col2"))

    def test_difficulty_check_aggregation(self):
        # with pytest.raises(difficulty_check.DifficultyNotImplemented):
        assert difficulty_check.difficulty_check_query(parse("SELECT COUNT(col1), col2 FROM table WHERE col1=2"))
        # with pytest.raises(difficulty_check.DifficultyNotImplemented):
        assert difficulty_check.difficulty_check_query(parse("SELECT min(col1), col2 FROM table WHERE col1=2"))

    def test_difficulty_check_nested(self):
        with pytest.raises(difficulty_check.DifficultyNotImplemented):
            difficulty_check.difficulty_check_query(
                parse("SELECT col1, col2 FROM table WHERE col1=in (SELECT col1 FROM table)"))
        with pytest.raises(difficulty_check.DifficultyNotImplemented):
            difficulty_check.difficulty_check_query(
                parse("SELECT col1, col2 FROM table WHERE col1=in (select col1 FROM table)"))

    def test_difficulty_check_expected(self):
        assert difficulty_check.difficulty_check_query(
            parse("SELECT col1, col2 FROM table WHERE col1=5"))


def read_cordis_queries():
    cordis_queries = []
    with open("tests/resources/cordis_integration_queries.tsv") as fd:
        rd = csv.reader(fd, delimiter="\t")
        _ = next(rd)  # Skip header
        for row in rd:
            cordis_queries.append([row[0], (row[1], row[2])])
    return cordis_queries


class TestQueryTransformationIntegration:
    @pytest.mark.parametrize('query,expected', read_cordis_queries())
    def test_transform_query_on_cordis(self, query: str, expected: Tuple[str, str]):
        assert query_pipeline.transform_query(query) == expected
