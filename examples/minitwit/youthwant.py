from bs4 import BeautifulSoup
from pprint import pprint
with open('a.html', 'r') as f:
    s = f.read()
soup = BeautifulSoup(s)
soup = soup.findAll("img", {"style": "max-width:600px"})
r = [i.get('src') for i in soup]
for u in r:
    print u
print '\n\n\n'



hs = ['<img src="%s" width="640" class="alignnone size-medium" />' % u for u in r]

i=0
for u in hs:
    print u
    i+=1
    if i%3 == 0 and i<len(hs):
        print
        print '<!--RndAds-->'
    print
