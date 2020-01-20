from utils import ChemrxivAPI, download_full, download_short


def main():
    api = ChemrxivAPI()
    download_short(api)
    download_full(api)


if __name__ == '__main__':
    main()
