import pytest

from visualizing.parent.table_process import parse_source, tokenize_table


class TestParentTableProcessing:
    def test_parse_source_expected(self):
        table_source = "<page_title> table title </page_title> <section_title> table section </section_title> " \
                       "<table> <cell> cell 1 <col_header> header 1 </col_header> </cell> <cell> " \
                       "cell 2 <col_header> header 2 </col_header> </cell> </table>"

        assert parse_source(table_source) == [
            ("header 1", "cell 1"),
            ("header 2", "cell 2"),
            ("title", "table title")
        ]

    def test_parse_source_blank_title(self):
        table_source = "<page_title>  </page_title> <section_title> table section </section_title> " \
                       "<table> <cell> cell 1 <col_header> header 1 </col_header> </cell> <cell> " \
                       "cell 2 <col_header> header 2 </col_header> </cell> </table>"

        assert parse_source(table_source) == [
            ("header 1", "cell 1"),
            ("header 2", "cell 2"),
            ("title", "")
        ]

    def test_parse_source_missing_header(self):
        table_source = "<page_title> table title </page_title> <section_title> table section </section_title> " \
                       "<table> <cell> cell 1 <col_header> header 1 </col_header> </cell> <cell> " \
                       "cell 2 <col_header>  </col_header> </cell> </table>"

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
