#!/usr/bin/env python3

import json
import os
from typing import Optional

import click
import requests
from tqdm import tqdm

HERE = os.path.abspath(os.path.dirname(__file__))
FIGSHARE_DIRECTORY = os.path.join(HERE, 'figshare')
os.makedirs(FIGSHARE_DIRECTORY, exist_ok=True)

institution_option = click.option('--institution', type=int, default=259)
directory_option = click.option('--directory', default=HERE, type=click.Path(file_okay=False, dir_okay=True))


class ChemrxivAPI:
    """Handle figshare API requests, using access token.

    Adapted from https://github.com/fxcoudert/tools/blob/master/chemRxiv/chemRxiv.py.
    """

    base = 'https://api.figshare.com/v2'

    def __init__(self, token=None, page_size: Optional[int] = None, institution: Optional[int] = None):
        if token is None:
            with open(os.path.expanduser('~/.config/figshare/chemrxiv.txt'), 'r') as file:
                token = file.read().strip()

        self.page_size = page_size or 500
        #: default of 259 corresponds to chemrxiv
        self.institution = institution or 259
        self.token = token
        self.headers = {'Authorization': f'token {self.token}'}

        self.articles_short_directory = os.path.join(FIGSHARE_DIRECTORY, str(self.institution), 'articles_short')
        self.articles_long_directory = os.path.join(FIGSHARE_DIRECTORY, str(self.institution), 'articles_long')

        r = requests.get(f'{self.base}/account', headers=self.headers)
        r.raise_for_status()

    def request(self, url, *, params=None):
        """Send a figshare API request."""
        return requests.get(url, headers=self.headers, params=params)

    def query(self, query, *, params=None):
        """Perform a direct query."""
        r = self.request(f'{self.base}/{query.lstrip("/")}', params=params)
        r.raise_for_status()
        return r.json()

    def query_generator(self, query, params=None):
        """Query for a list of items, with paging. Returns a generator."""
        if params is None:
            params = {}

        page = 1
        while True:
            params.update({'page_size': self.page_size, 'page': page})
            r = self.request(f'{self.base}/{query}', params=params)
            if r.status_code == 400:
                raise ValueError(r.json()['message'])
            r.raise_for_status()
            r = r.json()

            # Special case if a single item, not a list, was returned
            if not isinstance(r, list):
                yield r
                return

            # If we have no more results, bail out
            if len(r) == 0:
                return

            yield from r
            page += 1

    def all_preprints(self):
        """Return a generator to all the chemRxiv articles_short.

        .. seealso:: https://docs.figshare.com/#articles_list
        """
        return self.query_generator('articles', params={'institution': self.institution})

    def preprint(self, article_id):
        """Information on a given preprint.

        .. seealso:: https://docs.figshare.com/#public_article
        """
        return self.query(f'articles/{article_id}')

    def download_short(self) -> None:
        os.makedirs(self.articles_short_directory, exist_ok=True)
        for preprint in tqdm(self.all_preprints(), desc='Getting all articles_short'):
            preprint_id = preprint['id']
            path = os.path.join(self.articles_short_directory, f'{preprint_id}.json')
            if os.path.exists(path):
                continue
            with open(path, 'w') as file:
                json.dump(preprint, file, indent=2)

    def download_full(self) -> None:
        os.makedirs(self.articles_long_directory, exist_ok=True)
        for filename in tqdm(os.listdir(self.articles_short_directory)):
            preprint_id = int(filename[:-len('.json')])
            path = os.path.join(self.articles_long_directory, f'{preprint_id}.json')
            if os.path.exists(path):
                continue

            preprint = self.preprint(preprint_id)
            with open(path, 'w') as file:
                json.dump(preprint, file, indent=2)
