import csv
with open('pd.csv', 'rb') as f:
    lines = csv.reader(f)
    ps = []
    for line in lines:
        print line
        p = {}
        
        raw = [i.strip('\r').strip('\n').strip(' ') for i in line]
        p['desp'] = raw[0]
        p['vialid_time']= raw[1]
        p['incentive']= raw[2]
        p['publish_time']= raw[3]
        p['owner_name']= raw[4]
        p['icon']= raw[5]
        p['owner_title']= raw[6]
        p['company']= raw[7]
        p['logo']= raw[8]
        p['city'] = raw[9]
        p['country'] = raw[10]
        p['profile'] = raw[11]
        p['host'] = raw[12]
        p['join_time'] = raw[13]
        ps.append(p)

for p in ps:
    print p

