import sys
# sys.setdefaultencoding() does not exist, here!
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')
import json
import requests
from pprint import pprint

def getvu():
    headers = {
    'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ijg1ZGJlMTVkIn0.eyJhdWQiOiJhcGkudjIuc3dhZy5saXZlIiwic3ViIjoiNThiODIyMzU5NGFiNTZmOTEyNDViYjIwIiwiaXNzIjoiYXBpLnYyLnN3YWcubGl2ZSIsImV4cCI6MTUwMTM5MzI2NiwiaWF0IjoxNDk4ODAxMjY2LCJqdGkiOiJXVlhrY21pb1BnQ2g0d1N0In0._GeXeuEwtPCuP1Cqubr8h1fiITfSOvvuMxRW4t8bXpQ',
    'User-Agent': 'swag/2.6.1 (Android; com.machipopo.swag; Xiaomi; MI 3; en-US)',
    }

    params = (
    ('page', '1'),
    ('since', '1498814696'),
    ('limit', '64'),
    )

    r = requests.get('https://api.v2.swag.live/inbox', headers=headers, params=params)

#NB. Original query string below. It seems impossible to parse and
#reproduce query strings 100% accurately so the one below is given
#in case the reproduced version is not "correct".
# requests.get('https://api.v2.swag.live/inbox?page=1&since=1498814696&limit=64', headers=headers)

    x = json.loads(r.text)
    result = [(i['caption']['text'],i['media']['previewUrl']) for i in x]
    return result

x = getvu()
c=0
for u in x:
    c+=1
    print u
    print "<a href=%s>%s</a>"%(u[1],u[0])
    print ''
