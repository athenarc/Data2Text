import glob
import json

import requests
import yaml

with open('data/annotation/secret.yml', 'r') as stream:
    AUTH_TOKEN = yaml.safe_load(stream)['AUTH_TOKEN']

ANNOTATORS = [
    "Stavroula",
    "Giorgos",
    "Chris",
    "Katerina",
    "Antonis",
    "Anna",
    "Apostolis",
    "Mike"
]
ANNOTATIONS_DIR = 'storage/datasets/spider/annotations/label_studio/'


def get_all_projects():
    r = requests.get('https://darelab.imsi.athenarc.gr/qr2t_annotation/api/projects/',
                     headers={'Authorization': f'Token {AUTH_TOKEN}'}, )

    return json.loads(r.content)


def delete_all_projects():
    project_ids = [proj['id'] for proj in get_all_projects()['results']]

    for proj_id in project_ids:
        r = requests.delete(f'https://darelab.imsi.athenarc.gr/qr2t_annotation/api/projects/{proj_id}/',
                            headers={'Authorization': f'Token {AUTH_TOKEN}'})


def load_label_config():
    with open('data/annotation/label_studio_config.html', 'r') as file:
        config = file.read()
    return config


def create_project_parameters(annotator):
    return {
        "title": annotator,
        "label_config": load_label_config()
    }


def create_projects():
    for annotator in ANNOTATORS:
        _ = requests.post('https://darelab.imsi.athenarc.gr/qr2t_annotation/api/projects/',
                          headers={'Authorization': f'Token {AUTH_TOKEN}'},
                          json=create_project_parameters(annotator))


def match_file_names_with_id():
    projects = get_all_projects()['results']
    return {proj['title']: proj['id'] for proj in projects}


def import_data():
    for annotator, proj_id in match_file_names_with_id().items():
        with open(f'{ANNOTATIONS_DIR}{annotator}.json', 'r') as file:
            data = json.load(file)

        files = {'file': (f'{ANNOTATIONS_DIR}{annotator}.json', open(f'{ANNOTATIONS_DIR}{annotator}.json', 'r'))}

        res = requests.post(f'https://darelab.imsi.athenarc.gr/qr2t_annotation/api/projects/{proj_id}/import',
                            headers={'Authorization': f'Token {AUTH_TOKEN}'},
                            files=files)


if __name__ == '__main__':
    # print(">>> Deleting projects...", end='')
    # delete_all_projects()
    # print('Done')

    print(">>> Creating projects...", end='')
    create_projects()
    print('Done')

    print(">>> Importing tasks...", end='')
    import_data()
    print('Done')
