# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 23:04:04 2015

ImageCrawler

@author: Igor A. Stankevich
License: MIT

Dependencies: OpenCV, Pandas, Scikit-image, Pillow, Google API
"""

import os, random, time, socket
import pandas as pd
from apiclient.discovery import build as google_build
from multiprocessing.pool import ThreadPool
from crawler import save_images, purify

CX_KEY = 'YOUR_CX_HERE' # get it from https://developers.google.com/custom-search/ after creating Custom Search Engine
''' after creating engine enable image search '''

DEV_KEY = 'YOUR_DEV_KEY_HERE' # get it from https://console.developers.google.com/apis/

def save_cse_google_images(query, save_dir = 'crawled/API_googled/', min_width = 80, min_height = 80, verbose = True):
    # intializes google API Custom Search Engine
    sub_dir = query.replace(' ', '_')
    if not os.path.exists(save_dir + sub_dir):
        os.mkdir(save_dir + sub_dir)
    elif os.path.isfile(os.path.join(save_dir + sub_dir, 'ranks.csv')):
        if verbose:
            print '%s was already crawled, skipping...' % query
        return
    # used to not flood nameserver
    time.sleep(random.randint(1, 5))
    service = google_build("customsearch", "v1", developerKey=DEV_KEY)
    collection = service.cse()
    ranks = []
    if verbose:
        print 'Exact query: %s' % query
    # maximum 100 results per query allowed
    for i in xrange(1, 90, 10):
        if verbose:
            print 'Saving %s index %s ...' % (query, str(i))
        try:
            # sending request via google API
            result = collection.list(q=query, cx=CX_KEY, searchType='image', num=10, start=i).execute()
            images = [(item['link'], int(item['image']['height']), int(item['image']['width'])) for item in result['items']]
            if verbose:
                print 'Total images saving: %s ...' % str(len(images))
            save_images(i, images, ranks, save_dir, sub_dir, min_width, min_height, verbose=verbose)
        except Exception as e:
            if verbose:
                print 'Error: %s' % str(e)
    purify(save_dir + sub_dir + '/', verbose=verbose)
    if verbose:
        print 'Saving %s ...' % query
    rdf = pd.DataFrame(ranks, columns = ['File name', 'Score'])
    rdf.to_csv(save_dir + sub_dir + '/ranks.csv', index=False)
    
def main(file_ = 'newnames.csv'):
    people = pd.read_csv(file_, names=['Name'])
    people = list(people.Name.values)

    def generate_data(people):
        for person in people:
            yield person

    iterable = generate_data(people)
    pool = ThreadPool(4)
    pool.map(save_cse_google_images, iterable)
    pool.close()

if __name__ == '__main__':
    # setting connection timeout timer
    socket.setdefaulttimeout(60)
    main()