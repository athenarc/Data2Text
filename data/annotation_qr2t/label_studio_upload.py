import json

import requests
import yaml

with open('data/annotation_qr2t/secret.yml', 'r') as stream:
    AUTH_TOKEN = yaml.safe_load(stream)['AUTH_TOKEN']


def get_all_projects():
    r = requests.get('https://darelab.imsi.athenarc.gr/qr2t_annotation/api/projects/',
                     headers={'Authorization': f'Token {AUTH_TOKEN}'}, )

    return json.loads(r.content)


def delete_all_projects():
    project_ids = [proj['id'] for proj in get_all_projects()['results']]

    for proj_id in project_ids:
        _ = requests.delete(f'https://darelab.imsi.athenarc.gr/qr2t_annotation/api/projects/{proj_id}/',
                            headers={'Authorization': f'Token {AUTH_TOKEN}'})


def load_label_config(config_file):
    with open(config_file, 'r') as file:
        config = file.read()
    return config


def create_project_parameters(annotator, config_file):
    return {
        "title": annotator,
        "label_config": load_label_config(config_file)
    }


def create_projects(annotators, config_file):
    for annotator in annotators:
        _ = requests.post('https://darelab.imsi.athenarc.gr/qr2t_annotation/api/projects/',
                          headers={'Authorization': f'Token {AUTH_TOKEN}'},
                          json=create_project_parameters(annotator, config_file))


def match_file_names_with_id():
    projects = get_all_projects()['results']
    return {proj['title']: proj['id'] for proj in projects}


def import_data(annotations_dir):
    for annotator, proj_id in match_file_names_with_id().items():
        print(f'{annotations_dir}{annotator}.json')
        files = {'file': (f'{annotations_dir}{annotator}.json', open(f'{annotations_dir}{annotator}.json', 'r'))}

        _ = requests.post(f'https://darelab.imsi.athenarc.gr/qr2t_annotation/api/projects/{proj_id}/import',
                            headers={'Authorization': f'Token {AUTH_TOKEN}'},
                            files=files)


if __name__ == '__main__':
    ANNOTATORS = [
        "Stavroula",
        "George",
        "Chris",
        "Katerina",
        "Antonis",
        "Anna",
        "Mike"
    ]
    ANNOTATIONS_DIR = 'storage/datasets/cordis_inode/original/label_studio/not_labelled/'
    CONFIG_FILE = 'data/annotation_cordis/label_studio_config.html'

    print(">>> Deleting projects...", end='')
    delete_all_projects()
    print('Done')

    print(">>> Creating projects...", end='')
    create_projects(ANNOTATORS, CONFIG_FILE)
    print('Done')

    print(">>> Importing tasks...", end='')
    import_data(ANNOTATIONS_DIR)
    print('Done')
