#!/usr/bin/env python

import os
import arrow
import random
import urllib
import hashlib
import requests
import feedparser
from datetime import datetime

def calc_item_fingerprint(entry):
    if entry.get('guid'):
        return hashlib.sha1(entry.get('guid')).hexdigest()
    else:
        s = ''.join([entry.get('title', ''), entry.get('link', '')])
        s = s.encode('utf-8', 'ignore')
        return hashlib.sha1(s).hexdigest()

def calc_item_path(feed_url, item_fingerprint):
    feed_url_quoted = urllib.quote_plus(feed_url)
    parent_path = os.path.join('content', 'feeds', feed_url_quoted)
    if not os.path.isdir(parent_path):
        os.makedirs(parent_path)
    return os.path.join(parent_path, item_fingerprint + '.md')

def calc_item_pubdate(entry):
    for key in ['published_parsed', 'updated_parsed', 'created_parsed']:
        if key not in entry: continue
        if entry[key] is None: continue
        val = (entry[key])[:6]
        reported_timestamp = arrow.get(datetime(*val))
        if reported_timestamp < arrow.utcnow():
            return reported_timestamp
    return arrow.utcnow()

def process_feed(feed_url):
    try:
        print 'Requesting', feed_url
        response = requests.get(feed_url)
        response.raise_for_status()
    except:
        print '! Problem requesting', feed_url
        return

    parsed = feedparser.parse(response.text)
    feed_title = parsed.feed.get('title', 'Untitled Feed')
    if not feed_title:
        feed_title = 'Untitled Feed'

    for entry in parsed.entries:
        item_fingerprint = calc_item_fingerprint(entry)
        item_path = calc_item_path(feed_url, item_fingerprint)
        item_pubdate = calc_item_pubdate(entry)
        item_url = entry.get('link', '')

        if os.path.exists(item_path):
            continue

        print 'New item found, writing', item_path

        item_title = entry.get('title', '').encode('utf-8', 'ignore')
        item_title = item_title.replace('"', r'\"')
        with open(item_path, 'w') as fp:
            fp.write('+++\n')
            fp.write('date = "%s"\n' % str(arrow.utcnow()))
            fp.write('feedTitle = "%s"\n' % feed_title)
            fp.write('feedUrl = "%s"\n' % feed_url)
            fp.write('itemUrl = "%s"\n' % item_url)
            fp.write('publishDate = "%s"\n' % str(item_pubdate))
            fp.write('title = "%s"\n' % item_title)
            fp.write('+++\n')

def main(feeds):
    random.shuffle(feeds)
    for feed_url in feeds:
        process_feed(feed_url)

if __name__ == '__main__':
    feeds = [
        'http://techcrunch.com/feed/',
        'http://feeds.reuters.com/reuters/topNews',
        'http://www.cnbc.com/id/10000110/device/rss',
        'http://feeds.feedburner.com/nymag/intelligencer',
        'http://feeds.latimes.com/latimes/business',
        'http://feeds.feedburner.com/mediaite/ClHj',
        'http://splinternews.com/rss',
        'http://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/opinion/rss.xml',
        'http://hosted2.ap.org/atom/APDEFAULT/3d281c11a96b4ad082fe88aa0db04305',
        'http://www.axios.com/feeds/politics.rss',
        'http://www.politico.com/rss/politicopicks.xml',
    ]
    main(feeds)
