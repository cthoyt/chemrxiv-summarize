from typing import Optional

import click

from utils import (
    FigshareClient, plot_cumulative_authors, plot_cumulative_licenses,
    plot_first_time_first_authors_by_month, plot_gender_evolution, plot_gender_male_percentage, plot_papers_by_month,
    plot_prolific_authors, plot_unique_authors_per_month, plot_x, token_option,
)


@click.command()
@token_option
def main(token: Optional[str]):
    client = FigshareClient(token=token)
    df = client.get_df()

    plot_unique_authors_per_month(df, client.institution_directory, institution_name=client.institution_name)
    plot_papers_by_month(df, client.institution_directory, institution_name=client.institution_name)
    plot_x(df, client.institution_directory, institution_name=client.institution_name)
    plot_prolific_authors(df, client.institution_directory, institution_name=client.institution_name)
    plot_cumulative_authors(df, client.institution_directory, institution_name=client.institution_name)
    plot_cumulative_licenses(df, client.institution_directory, institution_name=client.institution_name)
    plot_first_time_first_authors_by_month(df, client.institution_directory, institution_name=client.institution_name)
    plot_gender_evolution(df, client.institution_directory, institution_name=client.institution_name)
    plot_gender_male_percentage(df, client.institution_directory, institution_name=client.institution_name)


if __name__ == '__main__':
    main()
