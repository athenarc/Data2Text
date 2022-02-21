import datetime
import json
import os

import requests
import yaml
from tqdm import tqdm

from data.annotation.label_studio_upload import AUTH_TOKEN, get_all_projects

ANNOTATION_STORE_DIR = 'storage/datasets/spider/annotations/label_studio/exports/'


def export_all_annotations():
    # Create the dir that we will store the exports
    today = datetime.datetime.now()
    date_time = today.strftime("%m_%d_%Y__%H_%M_%S")
    export_dir = ANNOTATION_STORE_DIR + date_time
    os.mkdir(export_dir)

    project_ids_titles = [(proj['id'], proj['title']) for proj in get_all_projects()['results']]
    for proj_id, title in tqdm(project_ids_titles):
        annotations = json.loads(
            requests.get(f'https://darelab.imsi.athenarc.gr/qr2t_annotation/api/projects/{proj_id}/export',
                         headers={'Authorization': f'Token {AUTH_TOKEN}'}).text)

        with open(f'{export_dir}/{title}.json', 'w') as outfile:
            json.dump(annotations, outfile)


if __name__ == '__main__':
    export_all_annotations()
