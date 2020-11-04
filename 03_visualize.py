import os
from typing import Optional

import click
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from utils import FigshareClient, HERE, prepare_genders, remove_current_month, token_option, assign_andy


def plot_papers_by_month(df, directory, institution_name):
    # How many papers each month?
    articles_by_month = df.groupby('time')['id'].count().reset_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=articles_by_month, x='time', y='id')
    plt.title(f'{institution_name} Articles per Month')
    plt.xlabel('Month')
    plt.ylabel('Articles')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'articles_per_month.png'), dpi=300)


def plot_unique_authors_per_month(df, directory, institution_name):
    # How many unique first authors each month?
    unique_authors_per_month = (
        df.groupby(['time', 'orcid'])
            .count()
            .reset_index().groupby('time')['id']
            .count()
            .reset_index()
    )
    plt.figure(figsize=(10, 6))
    sns.barplot(data=unique_authors_per_month, x='time', y='id')
    plt.title(f'{institution_name} Monthly Unique First Authorship')
    plt.xlabel('Month')
    plt.ylabel('Unique First Authors')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'unique_authors_per_month.png'), dpi=300)


def plot_x(df, directory, institution_name):
    rows = []
    articles_by_month = remove_current_month(df).groupby('time')['id'].count().reset_index()
    unique_authors_by_month = df.groupby(['time', 'orcid']).count().reset_index().groupby('time')['id'].count()
    for (d1, c1), (_d2, c2) in zip(unique_authors_by_month.reset_index().values, articles_by_month.values):
        rows.append((d1, 100 * (1 - c1 / c2)))
    data = pd.DataFrame(rows, columns=['time', 'percent'])
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=data, x='time', y='percent')
    plt.title(f'{institution_name} Percent Duplicate First Authors Each Month')
    plt.xlabel('Month')
    plt.ylabel('Percent Duplicate First Authors')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'percent_duplicate_authors_per_month.png'), dpi=300)


# TODO number new first authors each month

def plot_first_time_first_authors_by_month(df, directory, institution_name):
    data = df.groupby('orcid')['time'].min().reset_index().groupby('time')['orcid'].count().reset_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=data, x='time', y='orcid')
    plt.title(f'{institution_name} First Time First Authors per Month')
    plt.xlabel('Month')
    plt.ylabel('First Time First Authors')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'first_time_first_authors_per_month.png'), dpi=300)


def plot_prolific_authors(df, directory, institution_name):
    # Who's prolific in this institution?
    plt.figure(figsize=(10, 6))
    author_frequencies = df.groupby('orcid')['id'].count().sort_values(ascending=False).reset_index()
    sns.histplot(author_frequencies, y='id', kde=False, binwidth=4)
    plt.title(f'{institution_name} First Author Prolificness')
    plt.ylabel('First Author Frequency')
    plt.xlabel('Number of Articles Submitted')
    plt.xscale('log')
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'author_prolificness.png'), dpi=300)


def plot_cumulative_authors(df, directory, institution_name):
    # Cumulative number of unique authors over time. First, group by orcid and get first time
    author_first_submission = df.groupby('orcid')['time'].min()
    unique_historical_authors = author_first_submission.reset_index().groupby('time')['orcid'].count().cumsum()

    plt.figure(figsize=(10, 6))
    sns.lineplot(data=unique_historical_authors)
    plt.xticks(rotation=45)

    plt.title(f'{institution_name} Historical Unique First Time First Authorship')
    plt.ylabel('Cumulative Unique First Time First Authorship')
    plt.xlabel('Month')
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'historical_authorship.png'), dpi=300)


def plot_cumulative_licenses(df, directory, institution_name):
    # Cumulative number of licenses over time. First, group by orcid and get first time
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    for license, sdf in df.groupby('license'):
        historical_licenses = sdf.groupby('time').count()['id'].cumsum()
        sns.lineplot(data=historical_licenses, ax=ax, label=license)

    plt.xticks(rotation=45)
    plt.title(f'{institution_name} Historical Licenses')
    plt.ylabel('Cumulative Articles')
    plt.xlabel('Month')
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'historical_licenses.png'), dpi=300)


def plot_gender_evolution(df, directory, institution_name):
    plt.figure(figsize=(10, 6))

    df = prepare_genders(df)
    assign_andy(df)
    data = df.groupby(['time', 'first_author_inferred_gender']).count()['id'].reset_index()
    sns.lineplot(data=data, x='time', y='id', hue='first_author_inferred_gender')

    plt.xticks(rotation=45)
    plt.title(f'{institution_name} Inferred First Author Genders')
    plt.ylabel('Articles')
    plt.xlabel('Month')
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'genders_by_month.png'), dpi=300)


def plot_gender_male_percentage(df, directory, institution_name):
    plt.figure(figsize=(10, 6))
    df = prepare_genders(df)
    nd = df.groupby(['time', 'first_author_inferred_gender']).count()['id'].reset_index().pivot(
        index='time',
        columns='first_author_inferred_gender',
        values='id'
    ).fillna(0).astype(int)
    nd['ratio'] = (nd['male'] + 0.5 * nd['andy']) / (nd['male'] + nd['female'] + nd['andy'])
    sns.lineplot(data=nd, x='time', y='ratio')
    plt.xticks(rotation=45)
    plt.title(f'{institution_name} Inferred First Author Male Percentage')
    plt.ylabel('Male Percentage')
    plt.xlabel('Month')
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'male_percentage_by_month.png'), dpi=300)


@click.command()
@token_option
def main(token: Optional[str]):
    client = FigshareClient(token=token)
    df = client.get_df()

    plot_unique_authors_per_month(df, HERE, institution_name=client.institution_name)
    plot_papers_by_month(df, HERE, institution_name=client.institution_name)
    plot_x(df, HERE, institution_name=client.institution_name)
    plot_prolific_authors(df, HERE, institution_name=client.institution_name)
    plot_cumulative_authors(df, HERE, institution_name=client.institution_name)
    plot_cumulative_licenses(df, HERE, institution_name=client.institution_name)
    plot_first_time_first_authors_by_month(df, HERE, institution_name=client.institution_name)
    plot_gender_evolution(df, HERE, institution_name=client.institution_name)
    plot_gender_male_percentage(df, HERE, institution_name=client.institution_name)


if __name__ == '__main__':
    main()
