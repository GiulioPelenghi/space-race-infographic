#!/usr/bin/env python3
"""
process_space_data.py

Extracts, cleans, and standardizes orbital space launches from 1957 through September 2026
using Jonathan McDowell's General Catalog of Artificial Space Objects (GCAT).
Produces:
- data/launches_1957_2026.csv
- data/launches_grouped.json
- data/summary_stats.json
"""

import os
import csv
import json
from collections import defaultdict, Counter

LAUNCH_FILE = '/home/dcas/g.pelenghi/.gemini/antigravity/brain/dc6d3229-6a76-4033-8b6f-52287e482d54/.system_generated/steps/143/content.md'
ORGS_FILE = '/home/dcas/g.pelenghi/.gemini/antigravity/brain/dc6d3229-6a76-4033-8b6f-52287e482d54/.system_generated/steps/149/content.md'
AGENCIES_ORIG = '/home/dcas/g.pelenghi/Documents/antigravity/infographic/data/agencies_original.csv'

OUTPUT_CSV = '/home/dcas/g.pelenghi/Documents/antigravity/infographic/data/launches_1957_2026.csv'
OUTPUT_JSON = '/home/dcas/g.pelenghi/Documents/antigravity/infographic/data/launches_grouped.json'
OUTPUT_STATS = '/home/dcas/g.pelenghi/Documents/antigravity/infographic/data/summary_stats.json'

def load_orgs():
    orgs = {}
    with open(ORGS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = [c.strip() for c in line.strip().split('\t')]
            if len(parts) >= 6:
                code = parts[0]
                orgs[code] = {
                    'code': code,
                    'ucode': parts[1] if len(parts) > 1 else '',
                    'state_code': parts[2] if len(parts) > 2 else '',
                    'type': parts[3] if len(parts) > 3 else '',
                    'class': parts[4] if len(parts) > 4 else '',
                    'short_name': parts[7] if len(parts) > 7 else '',
                    'name': parts[8] if len(parts) > 8 else '',
                    'short_ename': parts[14] if len(parts) > 14 else '',
                    'ename': parts[15] if len(parts) > 15 else '',
                }
    return orgs

def load_original_agencies():
    agencies = {}
    if os.path.exists(AGENCIES_ORIG):
        with open(AGENCIES_ORIG, 'r', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                agencies[r['agency']] = r
    return agencies

def classify_agency(agency_raw, launch_year, orgs, orig_agencies):
    main_agency = agency_raw.split('/')[0] if '/' in agency_raw else agency_raw
    orig = orig_agencies.get(agency_raw) or orig_agencies.get(main_agency)
    org_info = orgs.get(agency_raw) or orgs.get(main_agency) or {}
    short_nm = org_info.get('short_name', agency_raw)
    
    # Soviet Union launches 1957-1991
    is_soviet_agency = agency_raw in ('RVSN', 'UNKS', 'GUKOS', 'MOM', 'MVS', 'VMFR') or main_agency in ('RVSN', 'UNKS', 'GUKOS', 'MOM', 'MVS', 'VMFR')
    if is_soviet_agency or (org_info.get('state_code') == 'SU') or (launch_year <= 1991 and agency_raw in ('RU', 'SU', 'RKA')):
        return {
            'agency_type': 'state',
            'provider_group': 'USSR',
            'state_code': 'SU',
            'display_name': 'Soviet Union (USSR)',
            'color_category': 'state_ussr'
        }
        
    # Russian Federation state (1992+)
    russian_state = {'FKA', 'Roskosmos', 'VKSR', 'KVR', 'VVKO', 'RVSNR', 'UNKSR', 'RAKA', 'RKA', 'KHRU', 'VMF'}
    if (agency_raw in russian_state or main_agency in russian_state) and launch_year >= 1992:
        return {
            'agency_type': 'state',
            'provider_group': 'Russia',
            'state_code': 'RU',
            'display_name': 'Roscosmos / Russian Military',
            'color_category': 'state_russia'
        }
        
    # US Government / Military / NASA
    us_state = {
        'NASA', 'USAF', 'AFSC', 'AFSSD', 'SAMSO', 'GSFC', 'JSC', 'MSFC', 'LERC', 'LARCN', 
        'AFSD', 'AFBMD', 'RSLP', 'NRL', 'AFSMC', 'AFSSD2', 'NOTS', 'USA', 'USN', 'ABMA', 
        'AFMC', '10ADS', '2SLS', '3SLS', '4SLS', 'S4300', 'S394I', 'USSF'
    }
    if agency_raw in us_state or main_agency in us_state or (orig and orig.get('state_code') == 'US' and orig.get('agency_type') == 'state'):
        return {
            'agency_type': 'state',
            'provider_group': 'United States',
            'state_code': 'US',
            'display_name': 'NASA / US Military',
            'color_category': 'state_us'
        }
        
    # China State
    china_state = {'CALT', 'SAST', 'CASC', 'CASIC', 'CASIC4A', 'PLA2AC'}
    if agency_raw in china_state or main_agency in china_state or (orig and orig.get('state_code') == 'CN' and orig.get('agency_type') == 'state'):
        return {
            'agency_type': 'state',
            'provider_group': 'China',
            'state_code': 'CN',
            'display_name': 'China (CASC / CALT / SAST)',
            'color_category': 'state_china'
        }
        
    # India State
    if agency_raw == 'ISRO' or main_agency == 'ISRO':
        return {
            'agency_type': 'state',
            'provider_group': 'India',
            'state_code': 'IN',
            'display_name': 'India (ISRO)',
            'color_category': 'state_india'
        }
        
    # Japan State
    japan_state = {'ISAS', 'NASDA', 'JAXA'}
    if agency_raw in japan_state or main_agency in japan_state:
        return {
            'agency_type': 'state',
            'provider_group': 'Japan',
            'state_code': 'J',
            'display_name': 'Japan (JAXA / ISAS / NASDA)',
            'color_category': 'state_japan'
        }
        
    # Europe State (ESA, CNES, ELDO)
    europe_state = {'ESA', 'CNES', 'ELDO', 'CRA', 'RAE'}
    if agency_raw in europe_state or main_agency in europe_state or (orig and orig.get('agency') in europe_state):
        return {
            'agency_type': 'state',
            'provider_group': 'Europe',
            'state_code': 'EU',
            'display_name': 'European State (ESA / CNES)',
            'color_category': 'state_europe'
        }
        
    # Commercial Providers
    # 1. SpaceX
    if agency_raw == 'SPX' or main_agency == 'SPX':
        return {
            'agency_type': 'private',
            'provider_group': 'SpaceX',
            'state_code': 'US',
            'display_name': 'SpaceX',
            'color_category': 'private_spacex'
        }
        
    # 2. Arianespace
    if agency_raw == 'AE' or main_agency == 'AE':
        return {
            'agency_type': 'private',
            'provider_group': 'Arianespace',
            'state_code': 'F',
            'display_name': 'Arianespace',
            'color_category': 'private_arianespace'
        }
        
    # 3. United Launch Alliance (ULA)
    if agency_raw in ('ULAL', 'ULAB', 'ULAD', 'ULA') or main_agency in ('ULAL', 'ULAB', 'ULAD', 'ULA'):
        return {
            'agency_type': 'private',
            'provider_group': 'ULA',
            'state_code': 'US',
            'display_name': 'United Launch Alliance (ULA)',
            'color_category': 'private_ula'
        }
        
    # 4. Rocket Lab
    if agency_raw in ('RLABN', 'RLABU', 'RLAB') or main_agency in ('RLABN', 'RLABU', 'RLAB'):
        return {
            'agency_type': 'private',
            'provider_group': 'Rocket Lab',
            'state_code': 'US',
            'display_name': 'Rocket Lab',
            'color_category': 'private_rocketlab'
        }
        
    # 5. Chinese Commercial
    chinese_commercial = {'XIDO', 'LANDSP', 'ZKYT', 'DFK', 'TIANB', 'XJRY', 'LYK', 'EXPACE', 'CZHJ', 'CGWIC'}
    if agency_raw in chinese_commercial or main_agency in chinese_commercial:
        name_map = {
            'XIDO': 'Galactic Energy',
            'LANDSP': 'LandSpace',
            'ZKYT': 'CAS Space',
            'DFK': 'Orienspace',
            'TIANB': 'Space Pioneer',
            'EXPACE': 'ExPace',
            'CZHJ': 'China Rocket Co.',
            'XJRY': 'i-Space'
        }
        sub = name_map.get(main_agency, 'China Commercial')
        return {
            'agency_type': 'private',
            'provider_group': 'China Commercial',
            'state_code': 'CN',
            'display_name': 'China Commercial (' + sub + ')',
            'color_category': 'private_china_commercial'
        }
        
    # 6. US Legacy Commercial
    us_legacy = {
        'MDSSC', 'BLS', 'LMA', 'MMA', 'LMSC', 'GDCLS', 'MMCLS', 
        'OSC', 'OSCC', 'OATK', 'OATKC', 'NGIS', 'NGISD', 'NGISC'
    }
    if agency_raw in us_legacy or main_agency in us_legacy:
        return {
            'agency_type': 'private',
            'provider_group': 'US Heritage Commercial',
            'state_code': 'US',
            'display_name': 'US Heritage (Boeing / Lockheed / Northrop / Orbital)',
            'color_category': 'private_us_heritage'
        }
        
    # 7. International Commercial
    intl_commercial = {
        'ILSK', 'ILSL', 'SEALP', 'SEALC', 'STSM', 'EUROK', 'MHI', 'RSC', 'PU', 
        'ELUS', 'EER', 'SPONE', 'ISAR', 'NSIL', 'INNOSP', 'GILM', 'SKYRT', 'GKLS'
    }
    if agency_raw in intl_commercial or main_agency in intl_commercial:
        return {
            'agency_type': 'private',
            'provider_group': 'International Commercial',
            'state_code': org_info.get('state_code', 'INTL'),
            'display_name': 'Intl Commercial (' + short_nm + ')',
            'color_category': 'private_intl_commercial'
        }
        
    # 8. US New Startups
    us_startups = {'ASTRV', 'FFLY', 'VORB', 'BLOR', 'RELSP', 'ABLSS'}
    if agency_raw in us_startups or main_agency in us_startups:
        return {
            'agency_type': 'private',
            'provider_group': 'US New Commercial',
            'state_code': 'US',
            'display_name': 'US New Space (' + short_nm + ')',
            'color_category': 'private_us_new'
        }
        
    # Fallback to org class
    org_class = org_info.get('class', '')
    if org_class == 'B':
        return {
            'agency_type': 'private',
            'provider_group': 'Other Commercial',
            'state_code': org_info.get('state_code', 'OTHER'),
            'display_name': short_nm,
            'color_category': 'private_other'
        }
    else:
        st = org_info.get('state_code') or (orig.get('state_code') if orig else 'OTHER')
        return {
            'agency_type': 'state',
            'provider_group': 'Other States',
            'state_code': st,
            'display_name': 'State (' + short_nm + ')',
            'color_category': 'state_other'
        }

def process():
    print("Loading organizations...")
    orgs = load_orgs()
    orig_agencies = load_original_agencies()
    
    print("Parsing launch database...")
    launches = []
    
    with open(LAUNCH_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = [c.strip() for c in line.strip().split('\t')]
            if len(parts) > 26:
                tag = parts[0]
                jd = parts[1]
                date_str = parts[2]
                lv_type = parts[3]
                variant = parts[4] if len(parts) > 4 else ''
                mission = parts[8] if len(parts) > 8 else ''
                site = parts[11] if len(parts) > 11 else ''
                agency_raw = parts[25]
                lcode = parts[26]
                
                # Check orbital
                if lcode and lcode[0] in ('O', 'D'):
                    year_str = date_str[:4]
                    if year_str.isdigit():
                        year = int(year_str)
                        if 1957 <= year <= 2026:
                            cat = 'O' if (lcode.startswith('OS') or lcode.startswith('DS')) else 'F'
                            c = classify_agency(agency_raw, year, orgs, orig_agencies)
                            
                            launch_record = {
                                'tag': tag,
                                'JD': jd,
                                'launch_date': date_str,
                                'launch_year': year,
                                'type': lv_type,
                                'variant': variant,
                                'mission': mission,
                                'site': site,
                                'agency_raw': agency_raw,
                                'agency': c['display_name'],
                                'provider_group': c['provider_group'],
                                'state_code': c['state_code'],
                                'category': cat,
                                'agency_type': c['agency_type'],
                                'color_category': c['color_category'],
                                'launch_code': lcode
                            }
                            launches.append(launch_record)
                            
    launches.sort(key=lambda x: float(x['JD']) if x['JD'] and x['JD'] != '-' else x['launch_year'])
    print("Total processed orbital launches (1957-2026): " + str(len(launches)))
    
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    fieldnames = [
        'tag', 'JD', 'launch_date', 'launch_year', 'type', 'variant', 'mission',
        'site', 'agency_raw', 'agency', 'provider_group', 'state_code',
        'category', 'agency_type', 'color_category', 'launch_code'
    ]
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(launches)
    print("Saved CSV: " + OUTPUT_CSV)
    
    PRIVATE_ORDER = [
        'SpaceX', 'Arianespace', 'ULA', 'Rocket Lab', 'China Commercial',
        'US Heritage Commercial', 'International Commercial', 'US New Commercial', 'Other Commercial'
    ]
    STATE_ORDER = [
        'USSR', 'Russia', 'United States', 'China', 'India', 'Japan', 'Europe', 'Other States'
    ]
    
    yearly_data = {}
    for year in range(1957, 2027):
        yearly_data[year] = {
            'year': year,
            'total': 0,
            'private_total': 0,
            'state_total': 0,
            'private_blocks': [],
            'state_blocks': []
        }
        
    for l in launches:
        y = l['launch_year']
        yearly_data[y]['total'] += 1
        if l['agency_type'] == 'private':
            yearly_data[y]['private_total'] += 1
        else:
            yearly_data[y]['state_total'] += 1

    for year in range(1957, 2027):
        year_launches = [l for l in launches if l['launch_year'] == year]
        
        # Private blocks
        private_launches = [l for l in year_launches if l['agency_type'] == 'private']
        private_by_prov = defaultdict(list)
        for l in private_launches:
            private_by_prov[l['provider_group']].append(l)
            
        for prov in PRIVATE_ORDER:
            if prov in private_by_prov:
                prov_list = private_by_prov[prov]
                success_count = sum(1 for x in prov_list if x['category'] == 'O')
                fail_count = sum(1 for x in prov_list if x['category'] == 'F')
                yearly_data[year]['private_blocks'].append({
                    'provider': prov,
                    'count': len(prov_list),
                    'success_count': success_count,
                    'fail_count': fail_count,
                    'color_category': prov_list[0]['color_category'],
                    'launches': prov_list
                })
                
        # State blocks
        state_launches = [l for l in year_launches if l['agency_type'] == 'state']
        state_by_prov = defaultdict(list)
        for l in state_launches:
            state_by_prov[l['provider_group']].append(l)
            
        for prov in STATE_ORDER:
            if prov in state_by_prov:
                prov_list = state_by_prov[prov]
                success_count = sum(1 for x in prov_list if x['category'] == 'O')
                fail_count = sum(1 for x in prov_list if x['category'] == 'F')
                yearly_data[year]['state_blocks'].append({
                    'provider': prov,
                    'count': len(prov_list),
                    'success_count': success_count,
                    'fail_count': fail_count,
                    'color_category': prov_list[0]['color_category'],
                    'launches': prov_list
                })
                
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(list(yearly_data.values()), f, indent=2)
    print("Saved JSON: " + OUTPUT_JSON)
    
    prov_totals = Counter(l['provider_group'] for l in launches)
    type_totals = Counter(l['agency_type'] for l in launches)
    outcome_totals = Counter(l['category'] for l in launches)
    
    stats = {
        'total_launches': len(launches),
        'start_year': 1957,
        'end_year': 2026,
        'latest_cutoff': '2026-09-06',
        'type_totals': dict(type_totals),
        'outcome_totals': dict(outcome_totals),
        'provider_totals': dict(prov_totals.most_common(20)),
        'spacex_total': prov_totals['SpaceX'],
        'china_commercial_total': prov_totals['China Commercial'],
        'rocket_lab_total': prov_totals['Rocket Lab'],
    }
    with open(OUTPUT_STATS, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    print("Saved stats: " + OUTPUT_STATS)
    print("\nSummary Statistics:")
    print(json.dumps(stats, indent=2))

if __name__ == '__main__':
    process()
