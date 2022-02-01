from app.backend.processing.process_query import clause_extractors


class TestClauseExtraction:
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

    def test_find_sel_cols_distinct_single_col(self):
        assert clause_extractors.find_sel_cols([{'value': {'distinct': {'value': 'col1'}}}]) \
               == {'col1'}

    def test_find_sel_cols_distinct_multiple_cols(self):
        assert clause_extractors.find_sel_cols([{'value': {'distinct': [{'value': 'c1'}, {'value': 't2.c2'}]}}]) \
               == {'c1', 't2.c2'}

    def test_find_sel_cols_distinct_with_aggr(self):
        assert clause_extractors.find_sel_cols(
            [{'value': {'count': {'distinct': {'value': 'c1'}}}}, {'value': 't2.c2'}]) == {'t2.c2'}

    def test_find_groupby_cols_single_col(self):
        assert clause_extractors.find_group_by_cols({'value': 'col1'}) == {'col1'}

    def test_find_groupby_cols_multiple_cols(self):
        assert clause_extractors.find_group_by_cols([{'value': 'col1'}, {'value': 'col2'}]) == {'col1', 'col2'}

    def test_find_groupby_cols_multiple_cols_table_alias(self):
        assert clause_extractors.find_group_by_cols([{'value': 't1.col1'}, {'value': 't2.col2'}]) \
               == {'t1.col1', 't2.col2'}

    def test_find_orderby_cols_single_col(self):
        assert clause_extractors.find_order_by_cols({'value': 'col1'}) == {'col1'}

    def test_find_orderby_cols_multiple_cols(self):
        assert clause_extractors.find_order_by_cols([{'value': 'col1'}, {'value': 'col2'}]) == {'col1', 'col2'}

    def test_find_orderby_cols_multiple_cols_table_alias(self):
        assert clause_extractors.find_order_by_cols([{'value': 't1.col1'}, {'value': 't2.col2'}]) \
               == {'t1.col1', 't2.col2'}

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

    def test_find_from_tables_with_joins(self):
        assert clause_extractors.find_from_tables(
            ['t1', {'join': 't2', 'on': {'eq': ['t1.id', 't2.id']}}]) == ['t1', 't2']
        assert clause_extractors.find_from_tables(
            ['t1', {'inner join': 't2', 'on': {'eq': ['t1.id', 't2.id']}}]) == ['t1', 't2']
        assert clause_extractors.find_from_tables(
            ['t1', {'left join': 't2', 'on': {'eq': ['t1.id', 't2.id']}}]) == ['t1', 't2']
        assert clause_extractors.find_from_tables(
            ['t1', {'left outer join': 't2', 'on': {'eq': ['t1.id', 't2.id']}}]) == ['t1', 't2']
        assert clause_extractors.find_from_tables(
            ['t1', {'right join': 't2', 'on': {'eq': ['t1.id', 't2.id']}}]) == ['t1', 't2']
        assert clause_extractors.find_from_tables(
            ['t1', {'right outer join': 't2', 'on': {'eq': ['t1.id', 't2.id']}}]) == ['t1', 't2']
        assert clause_extractors.find_from_tables(
            ['t1', {'full join': 't2', 'on': {'eq': ['t1.id', 't2.id']}}]) == ['t1', 't2']
        assert clause_extractors.find_from_tables(
            ['t1', {'full outer join': 't2', 'on': {'eq': ['t1.id', 't2.id']}}]) == ['t1', 't2']

    def test_find_from_tables_with_join_and_alias(self):
        assert clause_extractors.find_from_tables(
            ['t1', {'inner join': {'name': 'table2', 'value': 't2'}, 'on': {'eq': ['t1.id', 't2.id']}}]) == ['t1', 't2']

    def test_in_and_not_in_values_to_list_single_value_in_clause(self):
        clause = {'in': ['col1', {'literal': 'val1'}]}
        clause_extractors.in_and_not_in_values_to_list(clause)
        assert clause == {'in': ['col1', {'literal': ['val1']}]}

    def test_in_and_not_in_values_to_list_multiple_values_in_clause(self):
        clause = {'in': ['col1', {'literal': ['val1', 'val2', 'val3']}]}
        clause_extractors.in_and_not_in_values_to_list(clause)
        assert clause == {'in': ['col1', {'literal': ['val1', 'val2', 'val3']}]}

    def test_in_and_not_in_values_to_list_single_value_not_in_clause(self):
        clause = {'nin': ['col1', {'literal': 'val1'}]}
        clause_extractors.in_and_not_in_values_to_list(clause)
        assert clause == {'nin': ['col1', {'literal': ['val1']}]}

    def test_in_and_not_in_values_to_list_multiple_values_not_in_clause(self):
        clause = {'nin': ['col1', {'literal': ['val1', 'val2', 'val3']}]}
        clause_extractors.in_and_not_in_values_to_list(clause)
        assert clause == {'nin': ['col1', {'literal': ['val1', 'val2', 'val3']}]}
