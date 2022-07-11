import pytest

from visualizing.parent.table_process import parse_source, tokenize_table


class TestParentTableProcessing:
    def test_parse_source_expected(self):
        table_source = "<query> table query <table> table title " \
                       "<col0> header 1 | type | cell 1 " \
                       "<col2> header 2 | type | cell 2 "

        assert parse_source(table_source) == [
            ("header 1", "cell 1"),
            ("header 2", "cell 2"),
            ("title", "table title")
        ]

    def test_parse_source_blank_title(self):
        table_source = "<query> table query <table>  " \
                       "<col0> header 1 | type | cell 1 " \
                       "<col2> header 2 | type | cell 2 "

        assert parse_source(table_source) == [
            ("header 1", "cell 1"),
            ("header 2", "cell 2"),
            ("title", "")
        ]

    def test_parse_source_missing_header(self):
        table_source = "<query> table query <table> table title " \
                       "<col0> header 1 | type | cell 1 " \
                       "<col2>  | type | cell 2 "

        assert parse_source(table_source) == [
            ("header 1", "cell 1"),
            ("", "cell 2"),
            ("title", "table title")
        ]

    def test_table_tokenizer_expected(self):
        parsed_table = [
            ("Header 1", "cell 1"),
            ("header 2", "Cell 2"),
            ("title", "table title")
        ]

        assert tokenize_table(parsed_table) == [
            (["header", "1"], ["cell", "1"]),
            (["header", "2"], ["cell", "2"]),
            (["title"], ["table", "title"])
        ]
