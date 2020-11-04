import click

from utils import ChemrxivAPI, institution_option


@click.command()
@institution_option
def main(institution: int):
    api = ChemrxivAPI(institution=institution)
    api.download_short()
    api.download_full()


if __name__ == '__main__':
    main()
