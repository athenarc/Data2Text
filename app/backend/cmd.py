from app.backend.arg_parsing import get_model_config
from app.backend.query_results_explainer import QueryResultsExplainer


def main():
    cfg = get_model_config("CMD Data2Text")

    query_explainer = QueryResultsExplainer("storage/datasets/wiki_sql/raw/train.db", cfg)

    while True:
        query = input("Query: ")
        print(query_explainer.explain_query_results(query))


if __name__ == '__main__':
    main()
