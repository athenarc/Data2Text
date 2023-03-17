import json

import pandas as pd

from tools.human_evaluation.qr2t_benchmark.transform_to_label_studio import \
    parse_evaluation_point


def return_block_header(block_id):
    return f"[[Block:SQL{block_id + 1}]]"


def query_text(sql_query):
    return f"""
    [[Question:DB]]
    Query: <code>{sql_query}</code>
    <br>
    <br>
    <strong>Please rate the following translations</strong>
    """


def translation_matrix(translation, q_id):
    return f"""
    [[Question:Matrix]]
    [[ID:{q_id}]]
    {translation}

    [[Choices]]
    fluency level
    precision level
    [[Answers]]
    low
    average
    high
    """


def choose_correct_translation(q_id_logos, q_id_eqs):
    return f"""
    [[Question:MC:MultipleAnswer]]
    <strong>Choose the correct translation(s)</strong>
    [[Choices]]
    ${{q://{q_id_logos}/QuestionText}}
    ${{q://{q_id_eqs}/QuestionText}}
    """


def choose_better_translation(q_id_logos, q_id_eqs):
    return f"""
    [[Question:MC:SingleAnswer]]
    <strong>Which of the two translations do you like best?</strong>
    [[Choices]]
    ${{q://{q_id_logos}/QuestionText}}
    ${{q://{q_id_eqs}/QuestionText}}
    """


def create_single_block(block_id, sql_query, logos, eqsplain):
    logos_q_id = f"SQL{block_id + 1}.2"
    eqsplain_q_id = f"SQL{block_id + 1}.3"

    block = return_block_header(block_id) + \
            query_text(sql_query) + \
            translation_matrix(logos, logos_q_id) + \
            translation_matrix(eqsplain, eqsplain_q_id) + \
            choose_correct_translation(logos_q_id, eqsplain_q_id) + \
            choose_better_translation(logos_q_id, eqsplain_q_id)

    return block


def create_qualtrics_txt():
    df = pd.read_csv('./sql_to_text.csv', header=1)

    final_text = "[[AdvancedFormat]]\n\n"

    for block_id, result in df.iterrows():
        final_text += create_single_block(
            block_id=block_id,
            sql_query=result[0],
            logos=result[1],
            eqsplain=result[2]
        )
        final_text += '\n'

    # write
    with open("sql_to_text_qualtrics.txt", "w") as text_file:
        text_file.write(final_text)


if __name__ == '__main__':
    create_qualtrics_txt()
