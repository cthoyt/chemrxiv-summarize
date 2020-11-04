import json
import os

import click
import pandas as pd
from tqdm import tqdm

from utils import FIGSHARE_DIRECTORY, HERE, institution_option


@click.command()
@institution_option
def main(institution: int):
    institution_directory = os.path.join(FIGSHARE_DIRECTORY, str(institution))
    articles_long_directory = os.path.join(institution_directory, 'articles_long')

    rows = []
    for filename in tqdm(os.listdir(articles_long_directory)):
        path = os.path.join(articles_long_directory, filename)
        with open(path) as file:
            j = json.load(file)

        orcid = None
        for custom_field in j.get('custom_fields', []):
            if custom_field['name'] == 'ORCID For Submitting Author':
                orcid = custom_field['value']

        rows.append(dict(
            id=j['id'],
            title=j['title'],
            posted=j['timeline']['posted'],
            license=j['license']['name'],
            orcid=orcid,
        ))

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(institution_directory, 'articles_summary.tsv'), sep='\t', index=False)
    if institution == 259:
        df.to_csv(os.path.join(HERE, 'articles_summary.tsv'), sep='\t', index=False)


if __name__ == '__main__':
    main()
