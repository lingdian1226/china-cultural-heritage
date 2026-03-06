#!/usr/bin/env python3
"""第五批全国重点文物保护单位数据导入 (518项 + 3项增补, 2001年公布)"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from batch1_import import PROVINCE_CODE, PROVINCE_FULL

# 原始数据中省份名到 PROVINCE_CODE key 的映射
PROVINCE_RAW_MAP = {
    "北京市": "北京", "天津市": "天津", "上海市": "上海", "重庆市": "重庆",
    "河北省": "河北", "山西省": "山西", "辽宁省": "辽宁", "吉林省": "吉林",
    "黑龙江省": "黑龙江", "江苏省": "江苏", "浙江省": "浙江", "安徽省": "安徽",
    "福建省": "福建", "江西省": "江西", "山东省": "山东", "河南省": "河南",
    "湖北省": "湖北", "湖南省": "湖南", "广东省": "广东", "海南省": "海南",
    "四川省": "四川", "贵州省": "贵州", "云南省": "云南", "陕西省": "陕西",
    "甘肃省": "甘肃", "青海省": "青海",
    # 自治区用简称
    "内蒙古": "内蒙古", "广西": "广西", "西藏": "西藏", "宁夏": "宁夏", "新疆": "新疆",
}

# 3项增补
SUPPLEMENTS = [
    {"seq": 519, "id_num": "5-0519-1-145", "name": "里耶古城遗址", "era": "秦汉", "province_key": "湖南", "city": "龙山县", "category": "archaeological-sites"},
    {"seq": 520, "id_num": "5-0520-4-032", "name": "阿尔寨石窟", "era": "北朝至清", "province_key": "内蒙古", "city": "鄂托克旗", "category": "stone-carvings"},
    {"seq": 521, "id_num": "5-0521-5-041", "name": "焦裕禄烈士墓", "era": "1966年", "province_key": "河南", "city": "兰考县", "category": "modern-historic"},
]

def parse_raw_data(filepath):
    """解析 batch5_raw.txt 中 === 完整数据 === 之后的管道分隔行"""
    items = []
    reading = False
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "=== 完整数据 ===":
                reading = True
                continue
            if not reading or not line:
                continue
            parts = line.split("|")
            if len(parts) != 7:
                print(f"  ⚠️ 跳过格式错误行: {line}")
                continue
            seq, id_num, name, era, province_raw, city, category = parts
            province_key = PROVINCE_RAW_MAP.get(province_raw, province_raw)
            items.append({
                "seq": int(seq),
                "id_num": id_num,
                "name": name,
                "era": era,
                "province_key": province_key,
                "city": city,
                "category": category,
            })
    return items

def build_item(raw):
    code = PROVINCE_CODE[raw["province_key"]]
    return {
        "id": raw["id_num"],
        "name": raw["name"],
        "level": "national",
        "batch": 5,
        "category": raw["category"],
        "province": PROVINCE_FULL[code],
        "city": raw["city"],
        "district": "",
        "address": "",
        "era": raw["era"],
        "description": "",
        "historical_value": "",
        "sources": ["维基百科-第五批全国重点文物保护单位"],
        "last_updated": "2026-03-06",
        "data_quality": "basic",
        "contributors": ["iBo"]
    }

def main():
    raw_file = os.path.join(os.path.dirname(__file__), "batch5_raw.txt")
    items = parse_raw_data(raw_file)
    print(f"📄 从 batch5_raw.txt 解析到 {len(items)} 条数据")

    # 添加增补
    for sup in SUPPLEMENTS:
        items.append(sup)
    print(f"➕ 添加 {len(SUPPLEMENTS)} 条增补，共 {len(items)} 条")

    # 按省份分组
    by_province = {}
    for raw in items:
        code = PROVINCE_CODE[raw["province_key"]]
        by_province.setdefault(code, []).append(build_item(raw))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "national-level")
    os.makedirs(out_dir, exist_ok=True)

    total_new = 0
    files_updated = 0
    for code, new_items in sorted(by_province.items()):
        path = os.path.join(out_dir, f"{code}.json")
        existing = {}
        if os.path.exists(path):
            with open(path) as f:
                for item in json.load(f):
                    existing[item["id"]] = item
        new_count = 0
        for item in new_items:
            if item["id"] not in existing:
                existing[item["id"]] = item
                new_count += 1
                total_new += 1
        merged = sorted(existing.values(), key=lambda x: x["id"])
        with open(path, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
        if new_count > 0:
            files_updated += 1
        print(f"  {PROVINCE_FULL[code]} ({code}.json): {len(merged)} items total (+{new_count} new)")

    print(f"\n✅ 第五批 {len(items)} 项录入完成 (新增 {total_new} 项)")
    print(f"📁 更新了 {files_updated} 个省份JSON文件")

    # 分类统计
    print(f"\n📊 分类统计:")
    cats = {}
    for raw in items:
        cats[raw["category"]] = cats.get(raw["category"], 0) + 1
    for cat, count in sorted(cats.items()):
        print(f"    {cat}: {count}")

    print(f"\n🗺️ 涉及 {len(by_province)} 个省份")

if __name__ == "__main__":
    main()
