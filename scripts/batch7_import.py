#!/usr/bin/env python3
"""第七批全国重点文物保护单位数据导入 (1943项+1增补, 2013年公布)
维基百科将第七批数据分散在子页面中，需分别抓取各分类子页面。
"""
import json, os, sys, re, urllib.request, urllib.parse

sys.path.insert(0, os.path.dirname(__file__))
from batch1_import import PROVINCE_CODE, PROVINCE_FULL

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'national-level')

CAT_MAP = {
    '1': 'archaeological-sites',
    '2': 'ancient-tombs',
    '3': 'ancient-buildings',
    '4': 'stone-carvings',
    '5': 'modern-historic',
    '6': 'others',
}

PROVINCE_KEYWORDS = {
    '北京': '北京', '天津': '天津', '河北': '河北', '山西': '山西',
    '内蒙古': '内蒙古', '辽宁': '辽宁', '吉林': '吉林', '黑龙江': '黑龙江',
    '上海': '上海', '江苏': '江苏', '浙江': '浙江', '安徽': '安徽',
    '福建': '福建', '江西': '江西', '山东': '山东', '河南': '河南',
    '湖北': '湖北', '湖南': '湖南', '广东': '广东', '广西': '广西',
    '海南': '海南', '重庆': '重庆', '四川': '四川', '贵州': '贵州',
    '云南': '云南', '西藏': '西藏', '陕西': '陕西', '甘肃': '甘肃',
    '青海': '青海', '宁夏': '宁夏', '新疆': '新疆',
}

# Sub-page titles for each category
SUB_PAGES = [
    '第七批全国重点文物保护单位中的古遗址',
    '第七批全国重点文物保护单位中的古墓葬',
    '第七批全国重点文物保护单位中的古建筑',
    '第七批全国重点文物保护单位中的石窟寺及石刻',
    '第七批全国重点文物保护单位中的近现代重要史迹及代表性建筑',
    '第七批全国重点文物保护单位中的其他',
]

def detect_province(address):
    for kw, short in PROVINCE_KEYWORDS.items():
        if kw in address:
            return short
    return None

def get_city(address, province_kw=None):
    for kw in PROVINCE_KEYWORDS:
        if kw in address:
            idx = address.index(kw) + len(kw)
            rest = address[idx:]
            for suffix in ['维吾尔自治区', '壮族自治区', '回族自治区', '自治区', '省', '市']:
                if rest.startswith(suffix):
                    rest = rest[len(suffix):]
                    break
            city = rest.split('、')[0].split('，')[0].strip()
            return city if city else address
    return address

def fetch_page_html(title):
    """Fetch rendered HTML of a Wikipedia page"""
    encoded = urllib.parse.quote(title)
    url = f'https://zh.wikipedia.org/wiki/{encoded}'
    print(f"  Fetching: {title}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; heritage-bot/1.0)'})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        print(f"  ERROR fetching {title}: {e}")
        return ""

def parse_html_table(html, batch=7):
    """Parse entries from HTML table rows containing 7-xxxx pattern"""
    entries = []
    # Match table rows with heritage IDs
    pattern = re.compile(
        r'<td[^>]*>\s*(\d+)\s*</td>\s*'
        r'<td[^>]*>\s*(' + str(batch) + r'-\d{4}-\d-\d{3})\s*</td>\s*'
        r'<td[^>]*>(.*?)</td>\s*'
        r'<td[^>]*>(.*?)</td>\s*'
        r'<td[^>]*>(.*?)</td>',
        re.DOTALL
    )
    
    for m in pattern.finditer(html):
        seq = int(m.group(1))
        id_num = m.group(2)
        name = re.sub(r'<[^>]+>', '', m.group(3)).strip()
        era = re.sub(r'<[^>]+>', '', m.group(4)).strip()
        address = re.sub(r'<[^>]+>', '', m.group(5)).strip()
        
        # Clean up common artifacts
        name = name.replace('&#160;', ' ').replace('&amp;', '&').strip()
        era = era.replace('&#160;', ' ').strip()
        address = address.replace('&#160;', ' ').strip()
        
        cat_digit = id_num.split('-')[2]
        category = CAT_MAP.get(cat_digit, 'others')
        province = detect_province(address)
        city = get_city(address) if province else address
        
        entries.append({
            'seq': seq,
            'id_num': id_num,
            'name': name,
            'era': era,
            'province': province,
            'city': city,
            'category': category,
            'address': address,
        })
    
    return entries

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return {"province": "", "items": data}
            return data
    return {"province": "", "items": []}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    all_entries = []
    
    for page_title in SUB_PAGES:
        html = fetch_page_html(page_title)
        if not html:
            continue
        entries = parse_html_table(html, batch=7)
        print(f"  -> {len(entries)} entries from {page_title}")
        all_entries.extend(entries)
    
    # Add supplement: 八宝山革命公墓 (2014年增补)
    supplement = {
        'seq': 1944,
        'id_num': '7-1944-5-331',
        'name': '八宝山革命公墓',
        'era': '1950年',
        'province': '北京',
        'city': '石景山区',
        'category': 'modern-historic',
        'address': '北京市石景山区',
    }
    all_entries.append(supplement)
    
    print(f"\n总计解析: {len(all_entries)} 条 (含增补)")
    
    # Stats
    cat_counts = {}
    province_counts = {}
    no_province = []
    
    for e in all_entries:
        cat_counts[e['category']] = cat_counts.get(e['category'], 0) + 1
        if e['province']:
            province_counts[e['province']] = province_counts.get(e['province'], 0) + 1
        else:
            no_province.append(e)
    
    print("\n分类统计:")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    
    print(f"\n涉及 {len(province_counts)} 个省份")
    
    if no_province:
        print(f"\n⚠️  {len(no_province)} 条未识别省份:")
        for e in no_province[:20]:
            print(f"  {e['id_num']} {e['name']} - {e['address']}")
    
    # Write to JSON
    updated_files = set()
    new_count = 0
    
    for e in all_entries:
        if not e['province']:
            for kw, short in PROVINCE_KEYWORDS.items():
                if kw in e.get('address', ''):
                    e['province'] = short
                    break
        
        if not e['province']:
            print(f"SKIP: {e['id_num']} {e['name']}")
            continue
        
        code = PROVINCE_CODE.get(e['province'])
        if not code:
            print(f"SKIP (no code): {e['province']} - {e['name']}")
            continue
        
        filepath = os.path.join(DATA_DIR, f"{code}.json")
        data = load_json(filepath)
        
        if not data.get('province'):
            data['province'] = PROVINCE_FULL.get(e['province'], e['province'])
        
        existing_ids = {item['id'] for item in data.get('items', [])}
        if e['id_num'] in existing_ids:
            continue
        
        item = {
            "id": e['id_num'],
            "name": e['name'],
            "level": "national",
            "batch": 7,
            "category": e['category'],
            "province": PROVINCE_FULL.get(e['province'], e['province']),
            "city": e['city'],
            "era": e['era'],
        }
        
        if 'items' not in data:
            data['items'] = []
        data['items'].append(item)
        save_json(filepath, data)
        updated_files.add(code)
        new_count += 1
    
    print(f"\n✅ 新增 {new_count} 条记录")
    print(f"📁 更新了 {len(updated_files)} 个省份文件")
    return len(all_entries)

if __name__ == '__main__':
    total = main()
    print(f"\n总计: {total}")
