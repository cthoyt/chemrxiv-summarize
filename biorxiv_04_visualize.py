import os

import pandas as pd

from biorxiv_02_download_articles import BIORXIV_DIRECTORY
from utils import plot_cumulative_licenses, plot_gender_evolution, plot_gender_male_percentage, plot_papers_by_month


def get_df():
    df = pd.read_csv(os.path.join(BIORXIV_DIRECTORY, 'articles.tsv'), sep='\t')
    df['year'] = df['posted'].map(lambda x: int(x.split('-')[0]))
    df['month'] = df['posted'].map(lambda x: int(x.split('-')[1]))
    df['time'] = [f'{a - 2000}-{b:02}' for a, b in df[['year', 'month']].values]
    return df


def main():
    df = get_df()
    plot_papers_by_month(df, BIORXIV_DIRECTORY, 'biorxiv', figsize=(14, 6))
    plot_cumulative_licenses(df, BIORXIV_DIRECTORY, 'biorxiv', figsize=(14, 6))
    plot_gender_male_percentage(df, BIORXIV_DIRECTORY, 'biorxiv', figsize=(14, 6))
    plot_gender_evolution(df, BIORXIV_DIRECTORY, 'biorxiv', figsize=(14, 6))


if __name__ == '__main__':
    main()
