import re
from typing import Dict


def get_single_table_attribute(source: str, section: str) -> str:
    try:
        return re.search(fr".*<{section}>(.*)</{section}>", source).group(1)
    except AttributeError:
        return ""


def parse_totto_format(source: str) -> Dict[str, str]:
    # We parse each part of the datapoint separately
    ret_dict = {
        "page_title": get_single_table_attribute(source, "page_title"),
        "section_title": get_single_table_attribute(source, "section_title"),
        "cell_values": list(re.findall("<cell>(.*?)<col_header>", source)),
        "header_values": list(re.findall("<col_header>(.*?)</col_header>", source))
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

    html_section = html_section_creator(parsed_table["page_title"], parsed_table["section_title"])
    html_table = html_table_creator(parsed_table["header_values"], parsed_table["cell_values"])

    return html_section + html_table
