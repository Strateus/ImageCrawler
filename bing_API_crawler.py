# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 23:04:04 2015

ImageCrawler

@author: Igor A. Stankevich
License: MIT

Dependencies: OpenCV, Pandas, Scikit-image, Pillow
"""

import os, random, socket, time
import pandas as pd
from multiprocessing.pool import ThreadPool
from bing_search_api import BingSearchAPI 
from crawler import save_images, purify

PARALLEL_THREADS = 4
BING_KEY = 'INSERT_YOUR_KEY' # from https://datamarket.azure.com/dataset/bing/search

def save_bing_images(query, save_dir = 'crawled/binged/', min_width = 80, min_height = 80,
                     key=BING_KEY, verbose = True):
    bing = BingSearchAPI(key)
    sub_dir = query.replace(' ', '_')
    if not os.path.exists(save_dir + sub_dir):
        os.mkdir(save_dir + sub_dir)
    elif os.path.isfile(os.path.join(save_dir + sub_dir, 'ranks.csv')):
        print '%s was already crawled, skipping...' % query
        return
    # used to not flood nameserver
    time.sleep(random.randint(1, 5))
    ranks = []
    if verbose:
        print 'Exact query: %s' % query
    # maximum 1000 results per query allowed
    for i in xrange(0, 1000, 50):
        if verbose:
            print 'Saving %s index %s ...' % (query, str(i))
        try:
            # sending request via google API
            params = {'ImageFilters':'"Face:Face"', '$format': 'json', '$top': 1000, '$skip': i}
            result = bing.search('image', query, params).json()
            images = [(item['MediaUrl'], item['Height'], item['Width']) for item in result['d']['results'][0]['Image']]
            total_left = int(result['d']['results'][0]['ImageTotal']) - i - len(images)
            if verbose:
                print 'Total images saving: %s ...' % str(len(images))
            save_images(i, images, ranks, save_dir, sub_dir, min_width, min_height, verbose=verbose)
            if verbose:
                print 'Done'
            if total_left <= 0 and verbose:
                if verbose:
                    print 'Total images crawled: %s' % result['d']['results'][0]['ImageTotal']
                break
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
    pool = ThreadPool(PARALLEL_THREADS)
    pool.map(save_bing_images, iterable)
    pool.close()

if __name__ == '__main__':
    # setting connection timeout timer
    socket.setdefaulttimeout(60)
    main()