import re


def get_table_title(source: str) -> str:
    try:
        return re.search(r"<table> (.*?) <col", source).group(1)
    except AttributeError:
        return ""


def get_table_query(source: str) -> str:
    try:
        return re.search(r"<query> (.*?) <table>", source).group(1)
    except AttributeError:
        return ""


def parse_totto_format(source: str):
    # We parse each part of the datapoint separately
    ret_dict = {
        "title": get_table_title(source),
        "query": get_table_query(source),
        "cell_values": list(re.findall(r"> .*? \| .*? \| (.*?) ", source)),
        "columns": list(re.findall(r"> .*? \| .*? \| (.*?) ", source))
    }

    return ret_dict


def html_table_creator(headers, values):
    headers_list = [f"<th>{header}</th>" for header in headers]
    headers_html = "<tr>" + "".join(headers_list) + "</tr>"

    values_list = [f"<td>{value}</td>" for value in values]
    values_html = "<tr>" + "".join(values_list) + "</tr>"

    return "<table style=\"width:100%\">\n" + headers_html + values_html + "</table"


def html_section_creator(page_title, section_title):
    return f"<p><strong>Title:</strong> {page_title}</p>" \
           f"<p><strong>Section</strong>: {section_title}</p>"


def to_valid_html(source):
    parsed_table = parse_totto_format(source)

    html_section = html_section_creator(parsed_table["title"], parsed_table["query"])
    html_table = html_table_creator(parsed_table["columns"], parsed_table["cell_values"])

    return html_section + html_table
