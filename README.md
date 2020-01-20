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

## Charts

How many authors have contributed per month to ChemRxiv?
This only counts using the ORCID iDs of the first authors;
it's pretty inconsistent what other identifying information
is included in the metadata for each article.

![Unique Authors per Month](unique_authors_per_month.png)

If we aggregate that data, we can ask how man authors have
submitted lots of articles:

![Author Prolificness](author_prolificness.png)

Finally, we can take the first date of authorship for each
author then count at each month how many unique first time
authors there are. Then, we can use a cumulative sum to show
how many authors have contributed to ChemRxiv at any point in
time.

![Historical Authorship](historical_authorship.png)
