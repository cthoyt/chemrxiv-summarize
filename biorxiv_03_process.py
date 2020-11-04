import json
import os

import pandas as pd
from gender_guesser.detector import Detector
from tqdm import tqdm

from biorxiv_02_download_articles import ARTICLES_DIRECTORY, BIORXIV_DIRECTORY


def main():
    detector = Detector(case_sensitive=False)
    rows = []
    for name in tqdm(os.listdir(ARTICLES_DIRECTORY)):
        if not name.endswith('.json'):
            continue
        with open(os.path.join(ARTICLES_DIRECTORY, name)) as file:
            j = json.load(file)

        collection = j['collection']
        if not collection:
            tqdm.write(f'Empty collection for {name}')
            continue
        i = collection[0]
        authors = i['authors'].split(';')
        rows.append(dict(
            id=i['doi'],
            title=i['title'],
            first_author_name=authors[0],
            first_author_inferred_gender=fix_name(authors[0], detector),
            license=i['license'],
            category=i['category'].strip(),
            posted=i['date'],
            peer_reviewed=i['published'],
        ))

    df = pd.DataFrame(rows).sort_values('posted')
    df.to_csv(os.path.join(BIORXIV_DIRECTORY, 'articles.tsv'), sep='\t', index=False)

    i = (df['first_author_inferred_gender'] != 'unknown').sum()
    tqdm.write(f'Authors with assigned genders: {i}/{len(df.index)} ({i / len(df.index):.2%})')


def fix_name(s, detector):
    if ',' in s:
        return 'unknown'
    return detector.get_gender(s.split(' ')[0])


if __name__ == '__main__':
    main()
