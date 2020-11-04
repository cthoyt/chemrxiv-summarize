import datetime
import json
import os
from typing import Iterable, Tuple

import requests
from tqdm import tqdm

from biorxiv_01_download_days import BIORXIV_DIRECTORY, BIORXIV_METADATA_DIRECTORY

ARTICLES_DIRECTORY = os.path.join(BIORXIV_DIRECTORY, 'articles')
os.makedirs(ARTICLES_DIRECTORY, exist_ok=True)

ENDPOINT = 'https://api.biorxiv.org/details/biorxiv'


def main():
    for rpath, doi in _iter_rpaths():
        url = f'{ENDPOINT}/{doi}'
        response = requests.get(url)
        response_json = response.json()
        with open(rpath, 'w') as file:
            json.dump(response_json, file, indent=2)


def _iter_rpaths() -> Iterable[Tuple[str, str]]:
    paths = list(_iter_paths())
    for path in tqdm(paths, desc='Downloading article metadata', unit='date'):
        with open(path) as file:
            j = json.load(file)
        for entry in tqdm(j, leave=False):
            doi = entry['biorxiv_doi']
            rpath = os.path.join(ARTICLES_DIRECTORY, f'{doi.replace("/", "_").strip()}.json')
            if os.path.exists(rpath):
                continue
            yield rpath, doi


def _iter_paths() -> Iterable[str]:
    for year in range(2013, datetime.date.today().year):
        year_directory = os.path.join(BIORXIV_METADATA_DIRECTORY, str(year))
        for month in os.listdir(year_directory):
            month_directory = os.path.join(year_directory, month)
            for name in os.listdir(month_directory):
                if not name.endswith('.json'):
                    continue
                yield os.path.join(month_directory, name)


if __name__ == '__main__':
    main()
