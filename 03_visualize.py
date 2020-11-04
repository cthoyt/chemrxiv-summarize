import os

import click
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from utils import FIGSHARE_DIRECTORY, HERE, institution_option


def clean_orcid(x: str) -> str:
    x = x.strip()
    if x.startswith('000-'):
        return f'0{x}'
    for p in ('orcid.org/', 'https://orcid.org/', 'http://orcid.org/'):
        if x.startswith(p):
            return x[len(p):]
    return x


def get_df(directory: str) -> pd.DataFrame:
    df = pd.read_csv(os.path.join(directory, 'articles_summary.tsv'), sep='\t')
    null_orcid_idx = df.orcid.isna()
    df = df[~null_orcid_idx]

    df['orcid'] = df['orcid'].map(clean_orcid)

    bad_orcid_idx = ~df.orcid.str.startswith('0000')

    df = df[~bad_orcid_idx]

    df['year'] = df.posted.map(lambda x: int(x.split('-')[0]))
    df['month'] = df.posted.map(lambda x: int(x.split('-')[1]))
    df['time'] = [f'{a - 2000}-{b:02}' for a, b in df[['year', 'month']].values]
    return df


def plot_authors_by_month(df, directory):
    # How many unique first authors each month?
    authors_by_month = df.groupby('time')['orcid'].count().reset_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=authors_by_month, x='time', y='orcid')
    plt.title('ChemRxiv Monthly Unique First Authorship')
    plt.xlabel('Month')
    plt.ylabel('Unique First Authors')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'unique_authors_per_month.png'), dpi=300)


def plot_prolific_authors(df, directory):
    # Who's prolific on chemrxiv?
    plt.figure(figsize=(10, 6))
    author_frequencies = df.groupby('orcid')['id'].count().sort_values(ascending=False)
    sns.histplot(author_frequencies, kde=False, binwidth=4)
    plt.title('ChemRxiv First Author Prolificness')
    plt.ylabel('Frequency')
    plt.xlabel('Articles')
    plt.xscale('log')
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'author_prolificness.png'), dpi=300)


def plot_cumulative_authors(df, directory):
    # Cumulative number of unique authors over time. First, group by orcid and get first time
    author_first_submission = df.groupby('orcid')['time'].min()
    unique_historical_authors = author_first_submission.reset_index().groupby('time')['orcid'].count().cumsum()

    plt.figure(figsize=(10, 6))
    sns.lineplot(data=unique_historical_authors)
    plt.xticks(rotation=45)

    plt.title('ChemRxiv Historical Unique First Authorship')
    plt.ylabel('Unique First Authors')
    plt.xlabel('Month')
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'historical_authorship.png'), dpi=300)


def plot_cumulative_licenses(df, directory):
    # Cumulative number of licenses over time. First, group by orcid and get first time
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    for license, sdf in df.groupby('license'):
        historical_licenses = sdf.groupby('time').count()['id'].cumsum()
        sns.lineplot(data=historical_licenses, ax=ax, label=license)

    plt.xticks(rotation=45)
    plt.title('ChemRxiv Historical Licenses')
    plt.ylabel('Articles')
    plt.xlabel('Month')
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'historical_licenses.png'), dpi=300)


@click.command()
@institution_option
def main(institution: int):
    institution_directory = os.path.join(FIGSHARE_DIRECTORY, str(institution))
    df = get_df(institution_directory)

    od = HERE if institution == 259 else institution_directory

    plot_authors_by_month(df, od)
    plot_prolific_authors(df, od)
    plot_cumulative_authors(df, od)
    plot_cumulative_licenses(df, od)


if __name__ == '__main__':
    main()
