from app.backend.processing.process_query.query_injectors import (
    inject_column_aliases, inject_limit_1, inject_verbalised_aggregates)


class TestQueryInjectors:
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

    def test_get_from_mappings_with_join_no_alias(self):
        assert inject_column_aliases.get_from_mappings(
            ['t1', {'inner join': 't2', 'on': {'eq': ['t1.id', 't2.id']}}]) == {}

    def test_get_from_mappings_with_join_and_alias(self):
        assert inject_column_aliases.get_from_mappings(
            ['t1', {'inner join': {'name': 't2', 'value': 'table2'}, 'on': {'eq': ['t1.id', 't2.id']}}]) \
               == {'t2': 'table2'}

    def test_add_limit_1_limit_1_exists(self):
        assert inject_limit_1.add_limit_1({'select': [{'value': 'col_name'}], 'from': 'table_name', "limit": 1}) == \
               {'select': [{'value': 'col_name'}], 'from': 'table_name', "limit": 1}

    def test_add_limit_1_limit_not_exists(self):
        assert inject_limit_1.add_limit_1({'select': [{'value': 'col_name'}], 'from': 'table_name'}) == \
               {'select': [{'value': 'col_name'}], 'from': 'table_name', "limit": 1}

    def test_add_limit_1_limit_else_exists(self):
        assert inject_limit_1.add_limit_1({'select': [{'value': 'col_name'}], 'from': 'table_name', "limit": 5}) == \
               {'select': [{'value': 'col_name'}], 'from': 'table_name', "limit": 1}

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
