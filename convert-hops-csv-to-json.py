#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

import csv
import json
import sys

# 0 Name
# 1 Source
# 2 Origin
# 3 Type
# 4 Aroma
# 5 AA low
# 6 AA high
# 7 BA low
# 8 BA high
# 9 Co-Humulone low
# 10 Co-Humulone high
# 11 Oil (mls/100g)
# 12 Oil high
# 13 M low
# 14 M high
# 15 H low
# 16 H high
# 17 C low
# 18 C high
# 19 F low
# 20 F high
# 21 subs
# 22 Notes
# 23 Storage (%AA/6M/20°C) low
# 24 Storage (%AA/6M/20°C) high
# 25 Storage (%AA/6M/20°C) text

def convert(inn, out):
    csv_reader = csv.reader(inn)
    json_accum = []
    sub_map = {}
    for row in csv_reader:
        name = row[0]
        region = ''
        try:
            region = row[2]
        except IndexError:
            pass
        source = row[1]
        source_url = ''
        if source.startswith('http'):
            source_url = source
        json_accum.append({'model': 'app.SourcedHopDetails',
                           'pk': None,
                           'fields': {
                               'name': name,
                               'region': region,
                               'source': source,
                               'source_url': source_url
                               # , ... all the other details
                               }})
        subs = row[21].split(',')
        sub_map[name] = subs
    json.dump(json_accum, out, indent=4)

    for sub,subs in sub_map.iteritems():
        json.dump({'from': sub, 'to': subs}, out, indent=4)

if __name__ == '__main__':
    convert(sys.stdin, sys.stdout)

