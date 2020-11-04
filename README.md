# chemrxiv-summarize

Motivated by <blockquote class="twitter-tweet" data-partner="tweetdeck"><p lang="en" dir="ltr">makes me wonder about the stats at <a href="https://twitter.com/ChemRxiv?ref_src=twsrc%5Etfw">@ChemRxiv</a> <a href="https://t.co/Ml5X8F4ckJ">https://t.co/Ml5X8F4ckJ</a></p>&mdash; Egon Willighⓐgen (@egonwillighagen) <a href="https://twitter.com/egonwillighagen/status/1219193083792969728?ref_src=twsrc%5Etfw">January 20, 2020</a></blockquote>

this repo summarize usage of ChemRxiv by using Figshare's API endpoint.

I've already run the download script on 2020-11-02. The scripts
can be run in this order to get nice charts.

```bash
pip install -r requirements.txt
python 01_download.py
python 02_process.py
python 03_visualize.py
```

Downloading takes a bit of time (40 minutes, maybe?) but there's
a tqdm bar to keep you entertained in the mean time.

I did a full write-up on the experience of writing this code and the results
in [this blog post](https://cthoyt.com/2020/04/15/summarizing-chemrxiv.html).

**See also** the [ChemRxiv dashboard](https://chemrxiv-dashboard.github.io)
([source code](https://github.com/chemrxiv-dashboard/chemrxiv-dashboard.github.io))
that displays similar statistics and is automatically updated daily.

## Charts

How many papers were submitted each month to ChemRxiv?

![Articles per Month](articles_per_month.png)

How many unique authors have contributed per month to ChemRxiv?
This only counts using the ORCID iDs of the first authors;
it's pretty inconsistent what other identifying information
is included in the metadata for each article.

![Unique Authors per Month](unique_authors_per_month.png)

How many authors submitted more than once per month? This
chart shows spikes in August, which I will guess is when
most people are submitting before their summer breaks :) 

![Percent Duplicate Authors per Month](percent_duplicate_authors_per_month.png)

How many authors contributed for their first time each month?

![First Time First Authors per Month](first_time_first_authors_per_month.png)

How many first authors have historically contributed to ChemRxiv
at each month? We can take the first date of authorship for each
author then count at each month how many unique first time
authors there are. Then, we can use a cumulative sum to show
how many authors have contributed to ChemRxiv at any point in
time.

![Historical Authorship](historical_authorship.png)

If we aggregate that data, we can ask how many authors have
submitted lots of articles:

![Author Prolificness](author_prolificness.png)

### Licensing

The following chart shows the popularity of different licenses
over time:

![Historical Licenses](historical_licenses.png)

### Gender Related

The [gender-guesser](https://pypi.org/project/gender-guesser/) package
was used to infer authors' genders based on their first name. This
obviously comes with the caveat that some names can't be automatically
assigned to the male/female dichotomy. The "mostly male" and "mostly female"
results were respectively grouped with the male and female names, while
the androgenous and unknown names were excluded.

The first chart shows both the male and female first author frequencies
by month.

![Genders of First Authors by Month](genders_by_month.png.png)

This chart shows the percentage of male first authors with respect
to male + female first authors. It shows that even as the number of
submissions changes, the ratio still is quite skewed towards male
first authorship.

![Male Percentage by Month](male_percentage_by_month.png)
