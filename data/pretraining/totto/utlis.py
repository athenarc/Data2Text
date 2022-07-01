import re


def extract_concise_table_attributes(table):
    def extract_query():
        reg = r"<query> (.*?) <table>"
        return re.search(reg, table)[1]

    def extract_tables():
        reg = r"<table> (.*?) <col"
        return re.search(reg, table)[1]

    def extract_cells():
        cells_with_ind = table.split('<col')[1:]

        cells = [cell[2:-1] if cell[2] == '>' else cell[3:-1] for cell in cells_with_ind]
        return cells

    def extract_cell_attributes(cell):
        attributes = cell.split(' | ')

        for attribute in attributes:
            if attribute == '':
                raise IndexError("We do not allow dirty empty columns")

        return {
            'col': attributes[0],
            'type': attributes[1],
            'value': attributes[2]
        }

    ret_attributes = {
        "query": extract_query(),
        "table": extract_tables(),
        "cells": [extract_cell_attributes(cell) for cell in extract_cells()]
    }

    return ret_attributes


def serialize_table(table_attributes):
    table_content = ""
    for ind, cell in enumerate(table_attributes['cells']):
        def serialize_cell():
            return f"<col{ind}> {cell['col']} | {cell['type']} | {cell['value']} "

        table_content += serialize_cell()

    # Remove the last trailing space character
    table_content = table_content[:-1]

    return f"<query> {table_attributes['query']} <table> {table_attributes['table']} {table_content}"
