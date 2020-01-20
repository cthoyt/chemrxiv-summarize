# chemrxiv-summarize

Summarize usage of ChemRxiv by using Figshare's API endpoint.

I've already run the download script on 2020-01-20. The scripts
can be run in this order to get nice charts.

```bash
python 01_download.py
python 02_process.py
python 03_visualize.py
```

Downloading takes a bit of time (40 minutes, maybe?) but there's
a tqdm bar to keep you entertained in the mean time.
