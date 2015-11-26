# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 23:04:04 2015

@author: Igor A. Stankevich
"""

import urllib2, json, os, socket
import pandas as pd
from crawler import save_images, purify


def save_google_images(query, save_dir = 'crawled/google/', top_index = 64, min_width = 80, min_height = 80, verbose = True):
    if verbose:
        print 'Querying %s ...' % query
    query_list = [query.replace(' ', '%20'),
                  query.replace(' ', '%20') + '&imgtype=face',
                  query.replace(' ', '%20') + '%20person',
                  query.replace(' ', '%20') + '%20photos']
    sub_dir = query.replace(' ', '_')
    if not os.path.exists(save_dir + sub_dir):
        os.mkdir(save_dir + sub_dir)
    elif os.path.isfile(os.path.join(save_dir + sub_dir, 'ranks.csv')):
        if verbose:
            print '%s was already crawled, skipping...' % query
        return
    fetcher = urllib2.build_opener()
    ranks = []
    for q in query_list:
        if verbose:
            print 'Exact query: %s' % q
        # maximum 64 allowed
        for i in xrange(0, 64, 8):
            if verbose:
                print 'Saving %s index %s ...' % (query, str(i))
            try:
                searchUrl = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=" + q + "&rsz=8&start=" + str(i)
                f = fetcher.open(searchUrl)
                data = json.load(f)
                if data['responseStatus'] == 200:
                    images = [(link['unescapedUrl'], int(link['height']), int(link['width'])) for link in data['responseData']['results']]
                    if verbose:
                        print 'Total images saving: %s ...' % str(len(images))
                    save_images(i, images, ranks, save_dir, sub_dir, min_width, min_height, verbose = verbose)
            except Exception as e:
                print 'Error: %s' % str(e)
    purify(save_dir + sub_dir + '/', verbose=verbose)
    if verbose:
        print 'Saving %s ...' % query
    rdf = pd.DataFrame(ranks, columns = ['File name', 'Score'])
    rdf.to_csv(save_dir + sub_dir + '/ranks.csv', index=False)

def main(file_ = 'images.csv'):
    people = pd.read_csv(file_, names=['Name'])
    people = list(people.Name.values)
    for person in people:
        save_google_images(person)

    '''
    #prohibited by Google
    def generate_data(people):
        for person in people:
            yield person

    iterable = generate_data(people)
    pool = ThreadPool(4)
    pool.map(save_google_images, iterable)
    pool.close()
    '''

if __name__ == '__main__':
    socket.setdefaulttimeout(60)
    main()