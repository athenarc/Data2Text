import argparse

from app.backend.query_results_explainer import QueryResultsExplainer
from config import cfg


def main():
    parser = argparse.ArgumentParser(description="Data2Text CMD.")
    parser.add_argument(
        "--config_file", default="", help="path to config file", type=str
    )
    args = parser.parse_args()

    if args.config_file != "":
        cfg.merge_from_file(args.config_file)
    cfg.freeze()

    query_explainer = QueryResultsExplainer("storage/datasets/wiki_sql/raw/train.db", cfg)

    while True:
        query = input("Query: ")
        print(query_explainer.explain_query_results(query))


if __name__ == '__main__':
    main()
