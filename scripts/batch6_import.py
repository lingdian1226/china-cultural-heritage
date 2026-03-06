#!/usr/bin/env python3
"""第六批全国重点文物保护单位数据导入 (1081项, 2006年公布)
自动从维基百科抓取并解析数据，写入 data/national-level/{province_code}.json
"""
import json, os, sys, re, urllib.request, urllib.parse

sys.path.insert(0, os.path.dirname(__file__))
from batch1_import import PROVINCE_CODE, PROVINCE_FULL

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'national-level')

# Category mapping by 编号 middle digit
CAT_MAP = {
    '1': 'archaeological-sites',
    '2': 'ancient-tombs',
    '3': 'ancient-buildings',
    '4': 'stone-carvings',
    '5': 'modern-historic',
    '6': 'others',
}

# Province keyword -> short name for PROVINCE_CODE lookup
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

def detect_province(address):
    """从地址字段检测省份简称"""
    for kw, short in PROVINCE_KEYWORDS.items():
        if kw in address:
            return short
    return None

def get_city(address, province_kw):
    """从地址提取城市/县"""
    # Remove province prefix
    for kw in PROVINCE_KEYWORDS:
        if kw in address:
            idx = address.index(kw) + len(kw)
            # Skip suffixes like 省、市、自治区 etc
            rest = address[idx:]
            for suffix in ['维吾尔自治区', '壮族自治区', '回族自治区', '自治区', '省', '市']:
                if rest.startswith(suffix):
                    rest = rest[len(suffix):]
                    break
            # Take first city/county
            city = rest.split('、')[0].split('，')[0].strip()
            return city if city else address
    return address

def fetch_and_parse():
    """Fetch Wikipedia page and parse entries"""
    title = urllib.parse.quote('第六批全国重点文物保护单位')
    url = f'https://zh.wikipedia.org/w/index.php?title={title}&action=raw'
    print(f"Fetching {url}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode('utf-8')
    
    print(f"Got {len(raw)} chars of wikitext")
    
    # Parse table rows: look for lines like | 1 || 6-0001-1-001 || name || era || address
    # Wiki table format: |- then | col1 || col2 || ...
    entries = []
    
    # Match patterns like: | 序号 || 编号 || 名称 || 时代 || 地址
    # The raw wikitext uses |- for row separators and | or || for cells
    lines = raw.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Look for lines starting with | that contain 6-xxxx pattern
        if re.search(r'6-\d{4}-\d-\d{3}', line):
            # Extract all cells from this line and possibly continuation lines
            cells = []
            combined = line
            # Some entries span multiple lines
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('|-') and not re.search(r'6-\d{4}-\d-\d{3}', lines[j]) and not lines[j].strip().startswith('|}') and not lines[j].strip().startswith('!'):
                if lines[j].strip().startswith('|') and '||' not in lines[j]:
                    break
                combined += ' ' + lines[j].strip()
                j += 1
            
            # Split by || 
            parts = re.split(r'\|\|', combined)
            parts = [p.strip().lstrip('|').strip() for p in parts]
            
            # Clean wiki markup
            cleaned = []
            for p in parts:
                # Remove [[ ]] links
                p = re.sub(r'\[\[([^\]|]*\|)?([^\]]*)\]\]', r'\2', p)
                # Remove {{ }}
                p = re.sub(r'\{\{[^}]*\}\}', '', p)
                # Remove HTML tags
                p = re.sub(r'<[^>]+>', '', p)
                # Remove refs
                p = re.sub(r'<ref[^>]*>.*?</ref>', '', p)
                p = re.sub(r'<ref[^>]*/>', '', p)
                cleaned.append(p.strip())
            
            if len(cleaned) >= 5:
                seq_str = cleaned[0]
                id_num = cleaned[1]
                name = cleaned[2]
                era = cleaned[3]
                address = cleaned[4]
                
                # Validate
                if re.match(r'6-\d{4}-\d-\d{3}', id_num):
                    try:
                        seq = int(seq_str)
                    except:
                        seq = 0
                    
                    cat_digit = id_num.split('-')[2]
                    category = CAT_MAP.get(cat_digit, 'others')
                    province = detect_province(address)
                    city = get_city(address, province) if province else address
                    
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
        i += 1
    
    return entries

def fallback_parse_from_text():
    """Fallback: fetch rendered text version and parse"""
    url = 'https://zh.wikipedia.org/wiki/' + urllib.parse.quote('第六批全国重点文物保护单位')
    print(f"Fallback: fetching rendered page...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode('utf-8')
    
    # Extract text from tables - find all rows with 6-xxxx pattern
    entries = []
    # Simple regex to find table rows in HTML
    # Pattern: <td>seq</td><td>id</td><td>name</td><td>era</td><td>address</td>
    pattern = re.compile(
        r'<td[^>]*>\s*(\d+)\s*</td>\s*'
        r'<td[^>]*>\s*(6-\d{4}-\d-\d{3})\s*</td>\s*'
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
        
        cat_digit = id_num.split('-')[2]
        category = CAT_MAP.get(cat_digit, 'others')
        province = detect_province(address)
        city = get_city(address, province) if province else address
        
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
                return data
            return data.get('items', [])
    return []

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    # Try wikitext parse first, fallback to HTML
    entries = fetch_and_parse()
    if len(entries) < 1000:
        print(f"Wikitext parse got only {len(entries)} entries, trying HTML fallback...")
        entries2 = fallback_parse_from_text()
        if len(entries2) > len(entries):
            entries = entries2
    
    print(f"\nParsed {len(entries)} entries")
    
    if len(entries) < 1050:
        print(f"WARNING: Expected ~1081 entries, got {len(entries)}")
    
    # Stats
    cat_counts = {}
    province_counts = {}
    no_province = []
    
    for e in entries:
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
        for e in no_province[:10]:
            print(f"  {e['id_num']} {e['name']} - {e['address']}")
    
    # Write to JSON files
    updated_files = set()
    new_count = 0
    
    for e in entries:
        if not e['province']:
            # Try to assign based on address
            # Multi-province items go to first province mentioned
            for kw, short in PROVINCE_KEYWORDS.items():
                if kw in e.get('address', ''):
                    e['province'] = short
                    break
        
        if not e['province']:
            print(f"SKIP (no province): {e['id_num']} {e['name']}")
            continue
        
        code = PROVINCE_CODE.get(e['province'])
        if not code:
            print(f"SKIP (unknown province code): {e['province']} - {e['name']}")
            continue
        
        filepath = os.path.join(DATA_DIR, f"{code}.json")
        items = load_json(filepath)
        
        # Check for duplicate
        existing_ids = {item['id'] for item in items}
        if e['id_num'] in existing_ids:
            continue
        
        item = {
            "id": e['id_num'],
            "name": e['name'],
            "level": "national",
            "batch": 6,
            "category": e['category'],
            "province": PROVINCE_FULL.get(e['province'], e['province']),
            "city": e['city'],
            "era": e['era'],
        }
        
        items.append(item)
        save_json(filepath, items)
        updated_files.add(code)
        new_count += 1
    
    print(f"\n✅ 新增 {new_count} 条记录")
    print(f"📁 更新了 {len(updated_files)} 个省份文件")
    
    return len(entries)

if __name__ == '__main__':
    total = main()
    print(f"\n总计解析: {total} 条")
