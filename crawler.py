from gevent import monkey
monkey.patch_all()

import time
import requests
from gevent import pool, queue
from lxml import html
import gevent

startTime = time.time()
p = pool.Pool(32)
q = queue.Queue()
s = requests.Session()

q.put('https://en.wikipedia.org/wiki/Python_(programming_language)')
pages = 0

def get_links(r):
    url = q.get_nowait()
    print 'request sent for - ',url
    global pages
    r = s.get(url)

    if r.status_code == 200:
        tree = html.fromstring(r.text)
        title = tree.xpath('//*[@id="firstHeading"]/text()')
        links = tree.xpath('//*[@id="mw-content-text"]//a')
        print 'extacted - ', title, 'pages scraped =  ',pages
        pages = pages + 1
        for link in links:
            next_link = link.xpath('.//@href')[0]

            if next_link[0:6] == '/wiki/' and next_link[-4:-3] != '.':
                q.put_nowait('https://en.wikipedia.org' + next_link)

g = p.spawn(get_links,0)
p.start(g)
p.join()

while not q.empty() and not p.full():
        for x in xrange(0, min(q.qsize(), p.free_count())):
            g = p.spawn(get_links,0)
            p.start(g)
            print 'queue',q.qsize(),'pool',p.free_count()

p.join()
print ('The script took {0} second !'.format(time.time() - startTime))
