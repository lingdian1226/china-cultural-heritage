#!/usr/bin/env python3
"""合并所有省份 JSON 数据为 website/data.js"""
import json, glob, os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'national-level')
OUT_FILE = os.path.join(os.path.dirname(__file__), 'website', 'data.js')

all_items = []
for fpath in sorted(glob.glob(os.path.join(DATA_DIR, '*.json'))):
    with open(fpath, 'r', encoding='utf-8') as f:
        d = json.load(f)
    items = d.get('items', d) if isinstance(d, dict) else d
    for item in items:
        # Normalize: keep only needed fields
        all_items.append({
            'id': item.get('id', ''),
            'name': item.get('name', ''),
            'batch': item.get('batch', 0),
            'category': item.get('category', ''),
            'province': item.get('province', ''),
            'city': item.get('city', ''),
            'era': item.get('era', ''),
            'district': item.get('district', ''),
            'address': item.get('address', ''),
            'description': item.get('description', ''),
        })

os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
with open(OUT_FILE, 'w', encoding='utf-8') as f:
    f.write('const HERITAGE_DATA = ')
    json.dump(all_items, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';\n')

print(f'Generated {OUT_FILE}: {len(all_items)} items, {os.path.getsize(OUT_FILE)//1024} KB')
