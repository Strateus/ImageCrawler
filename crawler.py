# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 23:04:04 2015

ImageCrawler

@author: Igor A. Stankevich
License: MIT

Dependencies: OpenCV, Scikit-image, Pillow
"""

import urllib, urllib2, os, random, cv2, time
from PIL import Image
from multiprocessing.pool import ThreadPool
from skimage import io

def cv2pil(img):
    return Image.fromarray(img)

def save_images(index, images, ranks, save_dir, sub_dir, min_width, min_height, verbose):
    for j, image in enumerate(images):
        if image[1] >= min_height and image[2] >= min_width:
            if 'jpg' in image[0] or 'jpeg' in image[0] or 'JPG' in image[0]:
                ext = '.jpg'
            elif 'png' in image[0] or 'PNG' in image[0]:
                ext = '.png'
            elif 'gif' in image[0] or 'GIF' in image[0]:
                ext = '.gif'
            else:
                if verbose:
                    print 'Unknown extension: ', image[0]
                ext = '.jpg'
            fname = str(index) + '_' + str(j) + '_' + str(random.randint(1,9999999)) + ext
            try:
                if 'fotonin' in image[0] or 'blog.stuttgarter-zeitung.de' in image[0]:
                    # fotonin requires more complicated logic through mechanize
                    # DE blog uses password
                    continue
                else:
                    try:
                        img = io.imread(image[0])
                    except urllib2.URLError as e:
                        if 'Temporary failure in name resolution' in str(e.reason):
                            sleep_timer = random.randint(20, 40)
                            if verbose:
                                print 'DNS error, sleeping for %s secs...' % str(sleep_timer)
                            time.sleep(sleep_timer)
                            img = io.imread(image[0])
                        else:
                            if verbose:
                                print 'Image read error: %s' % str(e)
                            continue
                    try:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    except Exception:
                        if verbose:
                            print 'Color converting error with file %s, skipping conversion' % fname
                        pass
                img_name = save_dir + sub_dir +'/' + fname
                if ext == '.gif':
                    img = cv2pil(img)
                    img.save(img_name)
                else:
                    cv2.imwrite(img_name, img)
            except Exception as e:
                if verbose:
                    print 'Saving error (main) with file %s: %s' % (image[0], str(e)[:100])
                try:
                    urllib.urlretrieve(image[0], save_dir + sub_dir + '/' + fname)
                except Exception as e:
                    if verbose:
                        print 'Saving error (backup): %s' % str(e)[:100]
                    pass
            ranks.append((fname, index + j))

def purify(path, verbose = True):
    if verbose:
        print 'Purifying %s ...' % path
    files = [ f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) ]
    bad_files = []
    
    def generate_data(files):
        for i, f1 in enumerate(files):
            yield i, f1
    
    def worker(data):
        i, f1 = data
        #print f1
        if f1 in bad_files or f1 == 'ranks.csv':
            return
        im = cv2.imread(path + f1)
        if im is None:
            return
        h1 = cv2.calcHist([cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)], [0],None,[256],[0,256])
        for j in xrange(i+1, len(files)):
            f2 = files[j]
            if f2 in bad_files or f2 == 'ranks.csv':
                continue
            im = cv2.imread(path + f2)
            if im is None:
                bad_files.append(f2)
                continue
            h2 = cv2.calcHist([cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)], [0],None,[256],[0,256])
            dif = cv2.compareHist(h1, h2, cv2.cv.CV_COMP_CORREL)
            #print 'Slave: %s. Difference with %s: %s' % (f2, f1, str(dif))
            if dif >= 0.99:
                #print 'Appending duplicate: %s (copy of %s)' % (f2, f1)
                bad_files.append(f2)

    iterable = generate_data(files)
    pool = ThreadPool()
    pool.map(worker, iterable)
    pool.close()

    if verbose:
        print 'Removing bad files or %s ...' % path
    for f in bad_files:
        try:
            os.remove(path + f)
        except Exception as e:
            if verbose:
                print 'File is missing: %s, error: %s' % (f, str(e))
            pass
