#!/usr/bin/env python3

import json
import os

import requests
from tqdm import tqdm

HERE = os.path.abspath(os.path.dirname(__file__))
articles_short_directory = os.path.join(HERE, 'articles_short')
articles_long_directory = os.path.join(HERE, 'articles_long')


class ChemrxivAPI:
    """Handle figshare API requests, using access token.

    Adapted from https://github.com/fxcoudert/tools/blob/master/chemRxiv/chemRxiv.py.
    """

    base = 'https://api.figshare.com/v2'
    pagesize = 100

    def __init__(self, token=None):
        if token is None:
            with open(os.path.expanduser('~/.config/figshare/chemrxiv.txt'), 'r') as file:
                token = file.read().strip()

        #: corresponds to chemrxiv
        self.institution = 259
        self.token = token
        self.headers = {'Authorization': f'token {self.token}'}

        r = requests.get(f'{self.base}/account', headers=self.headers)
        r.raise_for_status()

    def request(self, url, *, params=None):
        """Send a figshare API request"""
        return requests.get(url, headers=self.headers, params=params)

    def query(self, query, *, params=None):
        """Perform a direct query"""
        r = self.request(f'{self.base}/{query.lstrip("/")}', params=params)
        r.raise_for_status()
        return r.json()

    def query_generator(self, query, method='get', params=None):
        """Query for a list of items, with paging. Returns a generator."""
        if params is None:
            params = {}
        n = 0
        while True:
            params.update({'limit': self.pagesize, 'offset': n})
            r = self.request(f'{self.base}/{query}', params=params)
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
            n += self.pagesize

    def all_preprints(self):
        """Return a generator to all the chemRxiv articles_short"""
        return self.query_generator(f'articles?institution={self.institution}')

    def preprint(self, identifier):
        """Information on a given preprint."""
        return self.query(f'articles/{identifier}')


def download_short(api):
    os.makedirs(articles_short_directory, exist_ok=True)
    for preprint in tqdm(api.all_preprints(), desc='Getting all articles_short'):
        preprint_id = preprint['id']
        with open(os.path.join(articles_short_directory, f'{preprint_id}.json'), 'w') as file:
            json.dump(preprint, file, indent=2)


def download_full(api):
    os.makedirs(articles_long_directory, exist_ok=True)
    for filename in tqdm(os.listdir(articles_short_directory)):
        preprint_id = int(filename[:-len('.json')])
        path = os.path.join(articles_long_directory, f'{preprint_id}.json')
        if os.path.exists(path):
            continue

        preprint = api.preprint(preprint_id)
        with open(path, 'w') as file:
            json.dump(preprint, file, indent=2)
