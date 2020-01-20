import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def clean_orcid(x):
    x = x.strip()
    if x.startswith('000-'):
        return f'0{x}'
    for p in ('orcid.org/', 'https://orcid.org/', 'http://orcid.org/'):
        if x.startswith(p):
            return x[len(p):]
    return x


def get_df():
    df = pd.read_csv('articles_summary.tsv', sep='\t')
    null_orcid_idx = df.orcid.isna()
    df = df[~null_orcid_idx]

    df['orcid'] = df['orcid'].map(clean_orcid)

    bad_orcid_idx = ~df.orcid.str.startswith('0000')

    df = df[~bad_orcid_idx]

    df['year'] = df.posted.map(lambda x: int(x.split('-')[0]))
    df['month'] = df.posted.map(lambda x: int(x.split('-')[1]))
    df['time'] = [f'{a - 2000}-{b:02}' for a, b in df[['year', 'month']].values]
    return df


def main():
    df = get_df()

    # How many unique first authors each month?

    authors_by_month = df.groupby('time')['orcid'].count().reset_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=authors_by_month, x='time', y='orcid')
    plt.title('ChemRxiv Monthly Unique Authorship')
    plt.xlabel('Month')
    plt.ylabel('Number Unique First Authors Submitting')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('unique_authors_per_month.png')

    # Who's prolific on chemrxiv?

    plt.figure(figsize=(10, 6))
    author_frequencies = df.groupby('orcid')['id'].count().sort_values(ascending=False)
    sns.distplot(author_frequencies, kde=False, hist_kws={'log': True})
    plt.title('ChemRxiv Author Prolificness')
    plt.ylabel('Frequency')
    plt.xlabel('Number of Articles Submitted to ChemRxiv')
    plt.tight_layout()
    plt.savefig('author_prolificness.png')

    # Cumulative number of unique authors over time. First, group by orcid and get first time

    author_first_submission = df.groupby('orcid')['time'].min()
    unique_historical_authors = author_first_submission.reset_index().groupby('time')['orcid'].count().cumsum()

    plt.figure(figsize=(10, 6))
    sns.lineplot(data=unique_historical_authors)
    plt.xticks(rotation=45)

    plt.title('ChemRxiv Historical Authorship')
    plt.ylabel('Historical First Authors')
    plt.xlabel('Month')
    plt.tight_layout()
    plt.savefig('historical_authorship.png')


if __name__ == '__main__':
    main()
