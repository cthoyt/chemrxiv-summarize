"""Get bioRxiv metadata.

.. seealso:: https://api.biorxiv.org/
"""

import datetime
import json
import logging
import os

import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)

HERE = os.path.abspath(os.path.dirname(__file__))
BIORXIV_DIRECTORY = os.path.join(HERE, 'biorxiv')
BIORXIV_METADATA_DIRECTORY = os.path.join(BIORXIV_DIRECTORY, 'metadata')
os.makedirs(BIORXIV_METADATA_DIRECTORY, exist_ok=True)

ENDPOINT = 'https://api.biorxiv.org/pub'

# The internet claims it went online in November 2013
STOP = datetime.date(year=2013, month=11, day=1)
INTERVAL = 100


def main():
    delta = datetime.timedelta(days=1)
    after = datetime.date.today()
    before = after - delta

    it = tqdm(desc='Downloading bioRxiv metadata', unit='days')
    while STOP < before:
        it.update()
        url = f'{ENDPOINT}/{before}/{after}'
        month_directory = os.path.join(BIORXIV_METADATA_DIRECTORY, str(after.year), f'{after.month:02}')
        os.makedirs(month_directory, exist_ok=True)

        date_str = f'{after.year}-{after.month:02}-{after.day:02}'
        path = os.path.join(month_directory, f'{date_str}.json')
        if not os.path.exists(path):
            rz = []
            page = 0
            it.set_postfix({'date': date_str})
            while True:
                response = requests.get(f'{url}/{page * INTERVAL}')
                response_json = response.json()
                message = response_json['messages'][0]
                if message.get('status') == 'no articles found':
                    break
                rz.extend(response_json['collection'])
                if message['count'] < INTERVAL:
                    break
                page += 1

            with open(path, 'w') as file:
                json.dump(rz, file, indent=2)

        before, after = before - delta, before


if __name__ == '__main__':
    main()
