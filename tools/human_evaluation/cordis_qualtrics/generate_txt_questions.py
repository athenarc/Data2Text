import json

from tools.human_evaluation.qr2t_benchmark.transform_to_label_studio import \
    parse_evaluation_point


def return_block_header(block_id):
    return f"[[Block:Verbalisation{block_id}]]"


def return_nl_query(nl_query):
    return f"""
    [[Question:DB]]
    <strong>NL Query</strong>
    <br>
    {nl_query}
    """


def return_query_results(table_names, query_results):
    styling = 'style="border: 1px solid black; padding: 12px; text-align: center"'
    results_str = f'<table {styling}>'

    results_str += f'<thead {styling}><tr>'
    for col_name in query_results.keys():
        results_str += f'<th {styling}><strong>{col_name}</strong></th>'
    results_str += "</tr ></thead>"

    results_str += f'<tbody {styling}><tr>'
    for val in query_results.values():
        results_str += f'<td {styling}>{val}</td>'
    results_str += "</tr></tbody>"
    results_str += "</table>"

    return f"""
    [[Question:DB]]
    <strong>Query Results</strong>
    <br><br>
    Table name(s): {table_names}
    {results_str}
    """


def return_verbalisation(verbalisation):
    return f"""
    [[Question:DB]]
    <strong>Verbalisation</strong>
    <br>
    {verbalisation}
    """


def return_correctness_question():
    return f"""
    [[Question:MC:SingleAnswer]]
    <strong>Correctness</strong>
    [[Choices]]
    Correct
    Incorrect
    """


def return_fluency_question():
    return f"""
    [[Question:MC:SingleAnswer]]
    <strong>Fluency</strong>
    [[Choices]]
    Perfect
    Adequate
    Not fluent
    """


def return_type_of_error():
    return f"""
    [[Question:Matrix]]
    <strong>Type of Error</strong>

    [[Choices]]
    Grammar or Syntax Error
    Omission
    Hallucination
    Other
    [[Answers]]
    0
    1
    2
    3
    4+
    """


def return_comment_text_entry():
    return f"""
    [[Question:TextEntry]]
    Comment (Optional)
    """


def create_single_block(block_id, annotation):
    block = return_block_header(block_id) + \
            return_nl_query(annotation['nl_query']) + \
            return_query_results(annotation['table_names'], annotation['query_results']) + \
            return_verbalisation(annotation['verbalisation']) + \
            return_correctness_question() + \
            return_fluency_question() + \
            return_type_of_error() + \
            return_comment_text_entry()

    return block


def create_qualtrics_txt():
    with open('cordis_inode.json', 'r') as file:
        results = json.load(file)

    final_text = "[[AdvancedFormat]]\n\n"

    for block_id, result in enumerate(results['data']):
        annotation = parse_evaluation_point(result[6])

        final_text += create_single_block(
            block_id,
            {
                'nl_query': annotation['nl_query'],
                'table_names': annotation['table_title'],
                'query_results': annotation['results_table'],
                'verbalisation': result[0]
            }
        )
        final_text += '\n'

    # write
    with open("cordis_qualtrics.txt", "w") as text_file:
        text_file.write(final_text)


if __name__ == '__main__':
    create_qualtrics_txt()
