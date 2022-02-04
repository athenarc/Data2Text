def filter_benchmark(datapoints):
    filters = [does_not_include_id]

    def passes_all_filters(datapoint):
        for filt in filters:
            if not filt(datapoint):
                return False
        return True

    return [datapoint for datapoint in datapoints if passes_all_filters(datapoint)]


def does_not_include_id(datapoint):
    id_tokens = [' id ', ' ID ', ' ids ']
    nl_question = ' ' + datapoint['question'].replace('.', ' ').replace(',', ' ').replace('?', ' ')

    return not any(id_tok in nl_question for id_tok in id_tokens)
