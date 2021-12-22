def create_table_title(title, page_title) -> str:
    if title == "":
        final_title = page_title
    elif page_title == "":
        final_title = title
    else:
        final_title = title \
            if len(title.split()) < len(page_title.split()) \
            else page_title

    return f"<page_title> {final_title} </page_title>"


def create_section_title(section) -> str:
    return f"<section_title> {section} </section_title>"


def create_col_cell(col, cell) -> str:
    return f"<cell> {cell} <col_header> {col} </col_header> </cell>"


def create_totto_table(table) -> str:
    cells = [create_col_cell(col, cell) for col, cell in zip(table['columns'], table['row'])]

    totto_table = f"{create_table_title(table['title'], table['pageTitle'])} " \
                  f"{create_section_title(table['section'])} " \
                  f"<table> {' '.join(cells)} </table>"

    return totto_table
