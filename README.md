# ImageCrawler
What this library can do:
- Crawls images through web search APIs
- Saves ranking of every image in ranks csv
- Eliminate image duplicates by comparing pairwise histograms

For now only Google API and Bing API implemented

<b>Note: add your keys and change save paths inside *_API_search.py files before usage.</b>

#Usage

Save your images' queries in <b>images.csv</b>, 1 per row.
Then run python script:

    python bing_API_search.py &

or

    python google_API_search.py &
