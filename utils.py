#!/usr/bin/env python3

import datetime
import json
import os
from typing import Optional

import click
import pandas as pd
import requests
from tqdm import tqdm

HERE = os.path.abspath(os.path.dirname(__file__))
FIGSHARE_DIRECTORY = os.path.join(HERE, 'figshare')
os.makedirs(FIGSHARE_DIRECTORY, exist_ok=True)

token_option = click.option('--token')
directory_option = click.option('--directory', default=HERE, type=click.Path(file_okay=False, dir_okay=True))


class FigshareClient:
    """Handle FigShare API requests, using an access token.

    Adapted from https://github.com/fxcoudert/tools/blob/master/chemRxiv/chemRxiv.py.
    """

    base = 'https://api.figshare.com/v2'

    def __init__(self, token: Optional[str] = None, page_size: Optional[int] = None):
        if token is None:
            with open(os.path.expanduser('~/.config/figshare/chemrxiv.txt'), 'r') as file:
                token = file.read().strip()

        self.page_size = page_size or 500
        self.token = token
        self.headers = {'Authorization': f'token {self.token}'}

        r = requests.get(f'{self.base}/account', headers=self.headers)
        r.raise_for_status()

        #: Got from https://docs.figshare.com/#private_institution_details
        institution_details = self.query('account/institution')
        self.institution = institution_details['id']
        self.institution_name = institution_details['name']

        self.institution_directory = os.path.join(FIGSHARE_DIRECTORY, str(self.institution))
        self.articles_short_directory = os.path.join(self.institution_directory, 'articles_short')
        self.articles_long_directory = os.path.join(self.institution_directory, 'articles_long')

    @classmethod
    def get_institution_name(cls, token=None) -> str:
        return cls(token=token).institution_name

    def request(self, url, *, params=None):
        """Send a FigShare API request."""
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

    def process_articles(self):
        from gender_guesser.detector import Detector
        detector = Detector(case_sensitive=False)
        # Possible gender determination alternatives:
        # - https://gender-api.com/ (reference from https://twitter.com/AdamSci12/status/1323977415677382656)
        # - https://genderize.io/

        rows = []
        for filename in tqdm(os.listdir(self.articles_long_directory)):
            path = os.path.join(self.articles_long_directory, filename)
            with open(path) as file:
                j = json.load(file)

            orcid = None
            for custom_field in j.get('custom_fields', []):
                if custom_field['name'] == 'ORCID For Submitting Author':
                    orcid = custom_field['value']

            first_author_name = j['authors'][0]['full_name']
            first_author_inferred_gender = detector.get_gender(first_author_name.split(' ')[0])

            rows.append(dict(
                id=j['id'],
                title=j['title'],
                posted=j['timeline']['posted'],
                license=j['license']['name'],
                orcid=orcid,
                first_author_name=first_author_name,
                first_author_inferred_gender=first_author_inferred_gender,
            ))

        df = pd.DataFrame(rows).sort_values('id')
        df.to_csv(os.path.join(self.institution_directory, 'articles_summary.tsv'), sep='\t', index=False)
        if self.institution == 259:
            df.to_csv(os.path.join(HERE, 'articles_summary.tsv'), sep='\t', index=False)

    def get_df(self):
        return get_df(self.institution_directory)


def get_df(directory: str, exclude_current_month: bool = False) -> pd.DataFrame:
    df = pd.read_csv(os.path.join(directory, 'articles_summary.tsv'), sep='\t')
    null_orcid_idx = df.orcid.isna()
    df = df[~null_orcid_idx]

    df['orcid'] = df['orcid'].map(clean_orcid)

    bad_orcid_idx = ~df.orcid.str.startswith('0000')

    df = df[~bad_orcid_idx]

    df['year'] = df.posted.map(lambda x: int(x.split('-')[0]))
    df['month'] = df.posted.map(lambda x: int(x.split('-')[1]))
    df['time'] = [f'{a - 2000}-{b:02}' for a, b in df[['year', 'month']].values]

    if exclude_current_month:
        df = remove_current_month(df)

    return df


def remove_current_month(df: pd.DataFrame) -> pd.DataFrame:
    today = datetime.date.today()
    df = df[df['time'] != f'{today.year - 2000}-{today.month:02}']
    return df


def prepare_genders(df: pd.DataFrame) -> pd.DataFrame:
    df = remove_current_month(df)
    df.loc[df['first_author_inferred_gender'] == 'mostly_male', 'first_author_inferred_gender'] = 'male'
    df.loc[df['first_author_inferred_gender'] == 'mostly_female', 'first_author_inferred_gender'] = 'female'
    return df


def assign_andy(df):
    x = (df['first_author_inferred_gender'] == 'andy').count()
    counter = 0

    def _assign_andy(s: str) -> str:
        if s != 'andy':
            return s
        if counter < x // 2:
            return 'male'
        return 'female'

    df['first_author_inferred_gender'] = df['first_author_inferred_gender'].map(_assign_andy)


def clean_orcid(x: str) -> str:
    x = x.strip().replace(' ', '').replace(';', '')
    if '-' not in x:
        print('PROBLEM with ORCiD', x)
    if x.startswith('000-'):
        return f'0{x}'
    for p in ('orcid.org/', 'https://orcid.org/', 'http://orcid.org/'):
        if x.startswith(p):
            return x[len(p):]
    return x
