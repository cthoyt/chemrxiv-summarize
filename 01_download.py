from typing import Optional

import click

from utils import FigshareClient, token_option


@click.command()
@token_option
def main(token: Optional[str]):
    api = FigshareClient(token=token)
    api.download_short()
    api.download_full()
    api.process_articles()


if __name__ == '__main__':
    main()
