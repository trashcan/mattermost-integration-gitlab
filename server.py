import os
import sys
import requests
import json
#import re
import time
import md5

import feedparser
import expiringdict 


USERNAME = ''
ICON_URL = ''
MATTERMOST_WEBHOOK_URL = '' # Paste the Mattermost webhook URL you created here
CHANNEL = '' # Leave this blank to post to the default channel of your webhook
RSS_URL = ''


def post_text(text):
    """
    Mattermost POST method, posts text to the Mattermost incoming webhook URL
    """

    data = {}
    data['text'] = text
    if len(USERNAME) > 0:
        data['username'] = USERNAME
    if len(ICON_URL) > 0:
        data['icon_url'] = ICON_URL
    if len(CHANNEL) > 0:
        data['channel'] = CHANNEL

    headers = {'Content-Type': 'application/json'}
    r = requests.post(MATTERMOST_WEBHOOK_URL, headers=headers, data=json.dumps(data))

    if r.status_code is not requests.codes.ok:
        print 'Encountered error posting to Mattermost URL %s, status=%d, response_body=%s' % (MATTERMOST_WEBHOOK_URL, r.status_code, r.json())


if __name__ == "__main__":
    MATTERMOST_WEBHOOK_URL = os.environ.get('MATTERMOST_WEBHOOK_URL', '')
    CHANNEL = os.environ.get('CHANNEL', CHANNEL)
    USERNAME = os.environ.get('USERNAME', USERNAME)
    ICON_URL = os.environ.get('ICON_URL', ICON_URL)
    RSS_URL = os.environ.get('RSS_URL', RSS_URL)

    if len(MATTERMOST_WEBHOOK_URL) == 0:
        print 'MATTERMOST_WEBHOOK_URL must be configured. Please see instructions in README.md'
        sys.exit()

    history = expiringdict.ExpiringDict(max_len=100000, max_age_seconds=86400*14)

    # Skip items present at start up
    rss = feedparser.parse(RSS_URL)
    for item in rss.entries:
	hash = md5.new(item.link).hexdigest()
    	history[hash] = True


    # Watch for new items
    while 1:
        rss = feedparser.parse(RSS_URL)
        
        c=0
	for item in rss.entries:
            hash = md5.new(item.link).hexdigest()
            if not history.get(hash):
                message = "[" + item.title + "](" + item.link + ")"
                post_text(message)
	    	history[hash] = True
	    c += 1	
	    if c == 10:
	        # There's a lot of junk at the bottom of HN that this ignores
	        break

 	time.sleep(60*5)    


