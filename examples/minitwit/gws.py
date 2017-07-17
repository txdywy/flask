# -*- coding: utf-8 -*-

def gen_dict_file():
    r = set()
    with open('/usr/share/dict/american-english', 'r') as f:
        a = f.readlines()
    a = set([i.strip('\n').lower() for i in a])
    with open('/usr/share/dict/british-english', 'r') as f:
        b = f.readlines()
    b = set([i.strip('\n').lower() for i in b])
    r = a.union(b)
    with open('gws.txt', 'w') as f:
        for i in r:
            f.write(i+'\n')
    print len(r)
