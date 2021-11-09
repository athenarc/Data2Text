import csv
from typing import Tuple

import pytest
from mo_sql_parsing import parse

from app.backend.db.SqliteController import SqliteController
from app.backend.processing.process_query import (clause_extractors,
                                                  difficulty_check,
                                                  query_pipeline)
from app.backend.processing.process_query.query_injectors import (
    inject_column_aliases, inject_from_where, inject_limit_1,
    inject_verbalised_aggregates)


class TestQueryProcessing:
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

    def test_add_limit_1_limit_1_exists(self):
        assert inject_limit_1.add_limit_1({'select': [{'value': 'col_name'}], 'from': 'table_name', "limit": 1}) == \
               {'select': [{'value': 'col_name'}], 'from': 'table_name', "limit": 1}

    def test_add_limit_1_limit_not_exists(self):
        assert inject_limit_1.add_limit_1({'select': [{'value': 'col_name'}], 'from': 'table_name'}) == \
               {'select': [{'value': 'col_name'}], 'from': 'table_name', "limit": 1}

    def test_add_limit_1_limit_else_exists(self):
        assert inject_limit_1.add_limit_1({'select': [{'value': 'col_name'}], 'from': 'table_name', "limit": 5}) == \
               {'select': [{'value': 'col_name'}], 'from': 'table_name', "limit": 1}

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

    def test_find_where_cols_simple(self):
        assert clause_extractors.find_where_cols({'eq': ['aa', 15]}) == {'aa'}

    def test_find_where_cols_complex(self):
        assert clause_extractors.find_where_cols({'or': [{'and': [{'eq': ['aa', 15]}, {'eq': ['bb', 12]}]},
                                                         {'gt': ['cc', 13]}]}) \
               == {'aa', 'bb', 'cc'}

    def test_find_sel_cols_list(self):
        assert clause_extractors.find_sel_cols([{'value': 'dd'}]) == {'dd'}
        assert clause_extractors.find_sel_cols([{'value': 'jobs.cc'}, {'value': 'dd'}]) == {'jobs.cc', 'dd'}

    def test_find_sel_cols_str(self):
        assert clause_extractors.find_sel_cols(['*']) == {'*'}

    def test_find_sel_cols_only_aggregate(self):
        assert clause_extractors.find_sel_cols([{'value': {'count': 'col1'}}]) == set()

    def test_find_sel_cols_multiple_aggregate(self):
        assert clause_extractors.find_sel_cols([{'value': {'count': 'col1'}}, {'value': {'sum': 'col2'}}]) \
               == set()

    def test_find_sel_cols_aggregate_and_col(self):
        assert clause_extractors.find_sel_cols([{'value': {'count': 'col1'}}, {'value': 'col2'}]) \
               == {'col2'}

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

    def test_find_from_tables_one_table_no_aliases(self):
        assert clause_extractors.find_from_tables('t1') == ['t1']

    def test_find_from_tables_multiple_tables_no_aliases(self):
        assert clause_extractors.find_from_tables(['t1', 't2']) == ['t1', 't2']

    def test_find_from_tables_one_table_with_alias(self):
        assert clause_extractors.find_from_tables({'value': 'table2', 'name': 't2'}) \
               == ['table2']

    def test_find_from_tables_multiple_tables_with_alias(self):
        assert clause_extractors.find_from_tables(
            [{'value': 'table1', 'name': 't1'}, {'value': 'table2', 'name': 't2'}]) \
               == ['table1', 'table2']

    def test_find_from_tables_multiple_tables_with_and_without_alias(self):
        assert clause_extractors.find_from_tables([{'value': 'table1', 'name': 't1'}, 'table2']) \
               == ['table1', 'table2']

    def test_get_from_mappings_one_table_no_aliases(self):
        assert inject_column_aliases.get_from_mappings('t1') == {}

    def test_get_from_mappings_multiple_tables_no_aliases(self):
        assert inject_column_aliases.get_from_mappings(['t1', 't2']) == {}

    def test_get_from_mappings_one_table_with_alias(self):
        assert inject_column_aliases.get_from_mappings({'value': 'table2', 'name': 't2'}) \
               == {'t2': 'table2'}

    def test_get_from_mappings_multiple_tables_with_alias(self):
        assert inject_column_aliases.get_from_mappings(
            [{'value': 'table1', 'name': 't1'}, {'value': 'table2', 'name': 't2'}]) \
               == {'t1': 'table1', 't2': 'table2'}

    def test_get_from_mappings_multiple_tables_with_and_without_alias(self):
        assert inject_column_aliases.get_from_mappings([{'value': 'table1', 'name': 't1'}, 'table2']) \
               == {'t1': 'table1'}

    def test_apply_join_aliases_single_table_no_alias(self):
        assert inject_column_aliases.apply_join_aliases({'select': [{'value': 'c'}], 'from': 't'}, ["t"]) \
               == {'select': [{'value': 'c'}], 'from': 't'}

    def test_apply_join_aliases_single_table_with_alias(self):
        assert inject_column_aliases.apply_join_aliases({'select': [{'value': 'c'}],
                                                         'from': {'value': 'table1', 'name': 't1'}},
                                                        ["table1"]) \
               == {'select': [{'value': 'c'}], 'from': {'value': 'table1', 'name': 't1'}}

    def test_apply_join_aliases_multiple_table_no_alias(self):
        assert inject_column_aliases.apply_join_aliases({'select': [{'value': 't1.c'}, {'value': 't2.c'}],
                                                         'from': ["t1", "t2"]},
                                                        ["t1", "t2"]) \
               == {'select': [{'value': 't1.c', 'name': 't1 c'},
                              {'value': 't2.c', 'name': 't2 c'}],
                   'from': ["t1", "t2"]}

    def test_apply_join_aliases_multiple_table_with_alias(self):
        assert inject_column_aliases.apply_join_aliases({'select': [{'value': 't1.c'}, {'value': 't2.c'}],
                                                         'from': [{'value': 'table1', 'name': 't1'},
                                                                  {'value': 'table2', 'name': 't2'}]},
                                                        ["table1", "table2"]) \
               == {'select': [{'value': 't1.c', 'name': 'table1 c'},
                              {'value': 't2.c', 'name': 'table2 c'}],
                   'from': [{'value': 'table1', 'name': 't1'},
                            {'value': 'table2', 'name': 't2'}]}

    def test_apply_join_aliases_multiple_table_with_and_without_alias(self):
        assert inject_column_aliases.apply_join_aliases({'select': [{'value': 't1.c'}, {'value': 'table2.c'}],
                                                         'from': [{'value': 'table1', 'name': 't1'},
                                                                  "table2"]},
                                                        ["table1", "table2"]) \
               == {'select': [{'value': 't1.c', 'name': 'table1 c'},
                              {'value': 'table2.c', 'name': 'table2 c'}],
                   'from': [{'value': 'table1', 'name': 't1'},
                            "table2"]}

    def test_apply_join_aliases_multiple_table_with_alias_only_aggr(self):
        assert inject_column_aliases.apply_join_aliases({'select': [{'value': {'count': 't2.c'}}],
                                                         'from': [{'value': 'table1', 'name': 't1'},
                                                                  {'value': 'table2', 'name': 't2'}]},
                                                        ["table1", "table2"]) \
               == {'select': [{'value': {'count': 't2.c'}}],
                   'from': [{'value': 'table1', 'name': 't1'},
                            {'value': 'table2', 'name': 't2'}]}

    def test_apply_join_aliases_multiple_table_with_alias_with_aggr(self):
        assert inject_column_aliases.apply_join_aliases({'select': [{'value': 't1.c'},
                                                                    {'value': {'count': 't2.c'}}],
                                                         'from': [{'value': 'table1', 'name': 't1'},
                                                                  {'value': 'table2', 'name': 't2'}]},
                                                        ["table1", "table2"]) \
               == {'select': [{'value': 't1.c', 'name': 'table1 c'},
                              {'value': {'count': 't2.c'}}],
                   'from': [{'value': 'table1', 'name': 't1'},
                            {'value': 'table2', 'name': 't2'}]}

    def test_verbalise_aggregates_single_table_single_col_avg(self):
        assert inject_verbalised_aggregates.verbalise_aggregates(
            {'select': [{'value': {'avg': 'col1'}}],
             'from': ['table1']},
            ["table1"]) \
               == {'select': [{'value': {'avg': 'col1'}, 'name': 'average col1'}],
                   'from': ['table1']}

    def test_verbalise_aggregates_single_table_two_cols_avg_sum(self):
        assert inject_verbalised_aggregates.verbalise_aggregates(
            {'select': [{'value': {'avg': 'col1'}},
                        {'value': {'sum': 'col2'}}],
             'from': ['table1']},
            ["table1"]) \
               == {'select': [{'value': {'avg': 'col1'}, 'name': 'average col1'},
                              {'value': {'sum': 'col2'}, 'name': 'sum of col2'}],
                   'from': ['table1']}

    def test_verbalise_aggregates_single_table_two_cols_max_none(self):
        assert inject_verbalised_aggregates.verbalise_aggregates(
            {'select': [{'value': {'avg': 'col1'}},
                        {'value': 'col2'}],
             'from': ['table1']},
            ["table1"]) \
               == {'select': [{'value': {'avg': 'col1'}, 'name': 'average col1'},
                              {'value': 'col2'}],
                   'from': ['table1']}

    def test_verbalise_aggregates_multiple_tables_single_col_min(self):
        assert inject_verbalised_aggregates.verbalise_aggregates(
            {'select': [{'value': {'avg': 'table1.col1'}}],
             'from': ['table1', 'table2']},
            ['table1', 'table2']) \
               == {'select': [{'value': {'avg': 'table1.col1'}, 'name': 'average col1'}],
                   'from': ['table1', 'table2']}

    def test_verbalise_aggregates_multiple_single_table_single_col_count(self):
        assert inject_verbalised_aggregates.verbalise_aggregates(
            {'select': [{'value': {'count': 'col1'}}],
             'from': ['table1']},
            ['table1']) \
               == {'select': [{'value': {'count': 'col1'}, 'name': 'count of table1'}],
                   'from': ['table1']}

    def test_verbalise_aggregates_multiple_multiple_table_single_col_count(self):
        assert inject_verbalised_aggregates.verbalise_aggregates(
            {'select': [{'value': {'count': 't1.col1'}}],
             'from': [{'value': 'table1', 'name': 't1'}, 'table2']},
            ['table1', 'table2']) \
               == {'select': [{'value': {'count': 't1.col1'}, 'name': 'count of table1'}],
                   'from': [{'value': 'table1', 'name': 't1'}, 'table2']}


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
