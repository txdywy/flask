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


def guess_word(pattern='',  letters=''):
    pattern, letters = pattern.lower(), letters.lower()
    with open('gws.txt', 'r') as f:
        ws = f.readlines()
    ws = [i.strip('\n') for i in ws]
    length = len(pattern)
    pt = {}
    for idx, i in enumerate(pattern):
        if i.isalpha():
            pt[idx] = i
    lets = set(letters)
    r = []
    for i in ws:
        f = True
        if len(i) ==  length:
            for x in i:
                if not lets:
                    continue
                if x not in lets:
                    f = False
                    break
        else:
            continue
        if f:
            ff = True
            for idx in pt:
                if pt[idx]!=i[idx]:
                    ff = False
                    break
            if ff:
                r.append(i)
    return r
