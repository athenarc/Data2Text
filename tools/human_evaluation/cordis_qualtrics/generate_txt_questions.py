import json

import pandas as pd

from tools.human_evaluation.qr2t_benchmark.transform_to_label_studio import \
    parse_evaluation_point


def return_block_header(block_id):
    return f"[[Block:Verbalisation{block_id + 1}]]"


def return_nl_query(nl_query):
    return f"""
    [[Question:DB]]
    <i>NL Query</i>
    <br>
    <br>
    {nl_query}
    """


def return_query_results(table_names, query_results):
    styling = 'style="border: 1px solid black; padding: 9px; text-align: center"'
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
    <i>Query Results</i>
    <br><br>
    Table name(s): {table_names}
    {results_str}
    """


def return_verbalisation(verbalisation):
    return f"""
    [[Question:DB]]
    <i>Verbalisation</i>
    <br>
    <br>
    {verbalisation}
    """


def return_correctness_question():
    return f"""
    [[Question:MC:SingleAnswer:Horizontal]]
    <strong>Is the verbalisation correct?</strong>
    [[Choices]]
    Yes
    No
    """


def return_correct_verbalisation_entry():
    return f"""
        [[Question:TextEntry:SingleLine]]
        <strong>Please write the correct verbalisation (optional)</strong>
        """


def return_fluency_question():
    return f"""
    [[Question:MC:SingleAnswer:Horizontal]]
    <strong>How fluent is the verbalisation?</strong>
    [[Choices]]
    Not fluent
    Adequate
    Fluent
    """


def return_type_of_error():
    return f"""
    [[Question:Matrix]]
    <strong>Choose how many times each error occurred</strong>

    [[Choices]]
    Grammar/Syntax Error
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
    [[Question:TextEntry:SingleLine]]
    <strong>Additional feedback (optional)</strong>
    """


def create_single_block(block_id, annotation):
    block = return_block_header(block_id) + \
            return_nl_query(annotation['nl_query']) + \
            return_query_results(annotation['table_names'], annotation['query_results']) + \
            return_verbalisation(annotation['verbalisation']) + \
            return_correctness_question() + \
            return_correct_verbalisation_entry() + \
            return_fluency_question() + \
            return_type_of_error() + \
            return_comment_text_entry()

    return block


def generate_csv_file():
    with open('cordis_inode.json', 'r') as file:
        results = json.load(file)['data']

    df_dict = {
        "nl_query": [],
        "sql_query": [],
        "results_verbalisation": [],
        "source": []
    }

    for res in results:
        annotation = parse_evaluation_point(res[6])
        df_dict['nl_query'].append(annotation['nl_query'])
        df_dict['sql_query'].append("")
        df_dict['results_verbalisation'].append(res[0])
        df_dict['source'].append(res[6])

    df = pd.DataFrame.from_dict(df_dict)

    df.to_csv('cordis_evaluation.csv')


def create_qualtrics_txt():
    df = pd.read_csv('./qr2t_cordis_bolzano.csv', header=1)

    final_text = "[[AdvancedFormat]]\n\n"

    for block_id, result in df.iterrows():
        annotation = parse_evaluation_point(result[3])

        final_text += create_single_block(
            block_id,
            {
                'nl_query': annotation['nl_query'],
                'table_names': annotation['table_title'],
                'query_results': annotation['results_table'],
                'verbalisation': result[2]
            }
        )
        final_text += '\n'

    # write
    with open("cordis_qualtrics.txt", "w") as text_file:
        text_file.write(final_text)


if __name__ == '__main__':
    create_qualtrics_txt()
