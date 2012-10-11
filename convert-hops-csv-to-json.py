#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

import csv
import json
import sys
from itertools import islice

# 0 Name
# 1 Source/Combined
# 2 Origin/Country
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

def safe_add(map, name, accessor):
    try:
        x = accessor();
        map[name] = x
    except Exception:
        pass

def safe_add_numeric(map, name, accessor):
    def _numeric():
        x = accessor()
        if x:
            return str(float(x))
        else:
            raise Exception()
    safe_add(map, name, _numeric)

def convert(inn, out):
    csv_reader = csv.reader(inn)
    json_accum = []
    hops = {}
    sub_map = {}
    for row in islice(csv_reader, 1, None):
        name = row[0]
        region = ''
        try:
            region = row[2]
            region = region.lower()
        except IndexError:
            pass
        source = row[1]
        source_url = ''
        if source.startswith('http'):
            source_url = source

        type = None
        try:
            type = row[3]
            if type == 'bittering':
                type = 'bitter'
            if type == '':
                type = None
        except IndexError:
            pass

        fields = {
            'name': name,
            'region': region,
            'source': source,
            'source_url': source_url
            }
        if type:
            fields['type'] = type

        safe_add_numeric(fields, 'alpha_acid_low', lambda: row[5])
        safe_add_numeric(fields, 'alpha_acid_high', lambda: row[6])
        safe_add_numeric(fields, 'beta_acid_low', lambda: row[7])
        safe_add_numeric(fields, 'beta_acid_high', lambda: row[8])
        safe_add_numeric(fields, 'cohumulone_pctg_low', lambda: row[9])
        safe_add_numeric(fields, 'cohumulone_pctg_high', lambda: row[10])
        safe_add_numeric(fields, 'oils_low', lambda: row[11])
        safe_add_numeric(fields, 'oils_high', lambda: row[12])
        safe_add_numeric(fields, 'myrcene_pctg_low', lambda: row[13])
        safe_add_numeric(fields, 'myrcene_pctg_high', lambda: row[14])
        safe_add_numeric(fields, 'humulene_pctg_low', lambda: row[15])
        safe_add_numeric(fields, 'humulene_pctg_high', lambda: row[16])
        safe_add_numeric(fields, 'caryophyllene_pctg_low', lambda: row[17])
        safe_add_numeric(fields, 'caryophyllene_pctg_high', lambda: row[18])
        safe_add_numeric(fields, 'farnesene_pctg_low', lambda: row[19])
        safe_add_numeric(fields, 'farnesene_pctg_high', lambda: row[20])
        safe_add_numeric(fields, 'storage_low', lambda: row[23])
        safe_add_numeric(fields, 'storage_high', lambda: row[24])

        desc = None
        try:
            desc = row[4]
            desc = desc.strip().strip('"')
            if len(desc) == 0:
                desc = None
        except IndexError:
            pass
        if desc:
            fields['desc'] = desc

        notes = None
        try:
            notes = row[22]
            notes = notes.strip().strip('"')
            if len(notes) == 0:
                notes = None
        except IndexError:
            pass
        if notes:
            fields['notes'] = notes

        json_accum.append({'model': 'app.SourcedHopDetails',
                           'pk': None,
                           'fields': fields})

        hops[name] = fields
        try:
            subs = [x.strip() for x in row[21].split(',')]
            sub_map[name] = subs
        except IndexError,e:
            pass # print str(e),row
    json.dump(json_accum, out, indent=4)

    for hop,subs in sub_map.iteritems():
        real_subs = []
        for sub in subs:
            exact = hops.has_key(sub)
            if exact:
                real_subs.append(sub)
            else:
                for key in hops:
                    if key.startswith(sub):
                        real_subs.append(key)
        if len(real_subs) == 0:
            print 'for %s unknown sub %s' % (hop,sub)
        else:
            for sub in real_subs:
                if False:
                    json.dump({'model': 'app.SourceHopSubstitution',
                               'from': hop, 'to': sub}, out, indent=4)

if __name__ == '__main__':
    convert(sys.stdin, sys.stdout)
