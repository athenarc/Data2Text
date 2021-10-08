from app.backend.controller.results_explainer import query_explainer


def main():
    # cfg = get_model_config("CMD Data2Text")

    # query_explainer = QueryResultsExplainer("storage/datasets/wiki_sql/raw/train.db", cfg)

    while True:
        query = input("Query: ")
        print(query_explainer.explain_query_results(query))


if __name__ == '__main__':
    main()
