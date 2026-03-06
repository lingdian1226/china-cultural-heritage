#!/usr/bin/env python3
"""第二批全国重点文物保护单位数据导入 (62项)"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from batch1_import import PROVINCE_CODE, PROVINCE_FULL

BATCH2 = [
    # 近现代重要史迹 (1-10)
    {"seq": 1, "id_num": "2-0001-5-001", "name": "林则徐销烟池与虎门炮台旧址", "era": "1839年", "province": "广东", "city": "东莞县", "category": "modern-historic"},
    {"seq": 2, "id_num": "2-0002-5-002", "name": "太平天国天王府遗址", "era": "1853至1864年", "province": "江苏", "city": "南京市", "category": "modern-historic"},
    {"seq": 3, "id_num": "2-0003-5-003", "name": "义和团吕祖堂坛口遗址", "era": "1900年", "province": "天津", "city": "天津市", "category": "modern-historic"},
    {"seq": 4, "id_num": "2-0004-5-004", "name": "安源路矿工人俱乐部旧址", "era": "1922年", "province": "江西", "city": "安源市", "category": "modern-historic"},
    {"seq": 5, "id_num": "2-0005-5-005", "name": "八七会议会址", "era": "1927年", "province": "湖北", "city": "武汉市", "category": "modern-historic"},
    {"seq": 6, "id_num": "2-0006-5-006", "name": "西安事变旧址", "era": "1936年", "province": "陕西", "city": "西安市", "category": "modern-historic"},
    {"seq": 7, "id_num": "2-0007-5-007", "name": "白求恩模范病室旧址", "era": "1938年", "province": "山西", "city": "五台县", "category": "modern-historic"},
    {"seq": 8, "id_num": "2-0008-5-008", "name": "西柏坡中共中央旧址", "era": "1948年", "province": "河北", "city": "平山县", "category": "modern-historic"},
    {"seq": 9, "id_num": "2-0009-5-009", "name": "北京宋庆龄故居", "era": "1963年", "province": "北京", "city": "北京市", "category": "modern-historic"},
    {"seq": 10, "id_num": "2-0010-5-010", "name": "宋庆龄墓", "era": "1981年", "province": "上海", "city": "上海市", "category": "modern-historic"},
    # 石窟寺 (11-15)
    {"seq": 11, "id_num": "2-0011-4-001", "name": "巩县石窟", "era": "北魏至宋", "province": "河南", "city": "巩县", "category": "stone-carvings"},
    {"seq": 12, "id_num": "2-0012-4-002", "name": "须弥山石窟", "era": "北朝至唐", "province": "宁夏", "city": "固原县", "category": "stone-carvings"},
    {"seq": 13, "id_num": "2-0013-4-003", "name": "乐山大佛", "era": "唐", "province": "四川", "city": "乐山市", "category": "stone-carvings"},
    {"seq": 14, "id_num": "2-0014-4-004", "name": "柏孜克里克千佛洞", "era": "唐至元", "province": "新疆", "city": "吐鲁番市", "category": "stone-carvings"},
    {"seq": 15, "id_num": "2-0015-4-005", "name": "飞来峰造像", "era": "五代至元", "province": "浙江", "city": "杭州市", "category": "stone-carvings"},
    # 古建筑 (16-43)
    {"seq": 16, "id_num": "2-0016-3-001", "name": "修定寺塔", "era": "唐", "province": "河南", "city": "安阳县", "category": "ancient-buildings"},
    {"seq": 17, "id_num": "2-0017-3-002", "name": "玉泉寺及铁塔", "era": "宋", "province": "湖北", "city": "当阳县", "category": "ancient-buildings"},
    {"seq": 18, "id_num": "2-0018-3-003", "name": "万部华严经塔", "era": "辽", "province": "内蒙古", "city": "呼和浩特市", "category": "ancient-buildings"},
    {"seq": 19, "id_num": "2-0019-3-004", "name": "华林寺大殿", "era": "宋", "province": "福建", "city": "福州市", "category": "ancient-buildings"},
    {"seq": 20, "id_num": "2-0020-3-005", "name": "开元寺", "era": "宋至清", "province": "福建", "city": "泉州市", "category": "ancient-buildings"},
    {"seq": 21, "id_num": "2-0021-3-006", "name": "灵岩寺", "era": "唐至清", "province": "山东", "city": "长清县", "category": "ancient-buildings"},
    {"seq": 22, "id_num": "2-0022-3-007", "name": "玄妙观三清殿", "era": "宋", "province": "江苏", "city": "苏州市", "category": "ancient-buildings"},
    {"seq": 23, "id_num": "2-0023-3-008", "name": "岩山寺", "era": "金", "province": "山西", "city": "繁峙县", "category": "ancient-buildings"},
    {"seq": 24, "id_num": "2-0024-3-009", "name": "北岳庙", "era": "元", "province": "河北", "city": "曲阳县", "category": "ancient-buildings"},
    {"seq": 25, "id_num": "2-0025-3-010", "name": "紫霄宫", "era": "明", "province": "湖北", "city": "均县", "category": "ancient-buildings"},
    {"seq": 26, "id_num": "2-0026-3-011", "name": "显通寺", "era": "明至清", "province": "山西", "city": "五台县", "category": "ancient-buildings"},
    {"seq": 27, "id_num": "2-0027-3-012", "name": "哲蚌寺", "era": "明", "province": "西藏", "city": "拉萨市", "category": "ancient-buildings"},
    {"seq": 28, "id_num": "2-0028-3-013", "name": "色拉寺", "era": "明", "province": "西藏", "city": "拉萨市", "category": "ancient-buildings"},
    {"seq": 29, "id_num": "2-0029-3-014", "name": "皇史宬", "era": "明", "province": "北京", "city": "北京市", "category": "ancient-buildings"},
    {"seq": 30, "id_num": "2-0030-3-015", "name": "悬空寺", "era": "明", "province": "山西", "city": "浑源县", "category": "ancient-buildings"},
    {"seq": 31, "id_num": "2-0031-3-016", "name": "天一阁", "era": "明至清", "province": "浙江", "city": "宁波市", "category": "ancient-buildings"},
    {"seq": 32, "id_num": "2-0032-3-017", "name": "古观象台", "era": "明至清", "province": "北京", "city": "北京市", "category": "ancient-buildings"},
    {"seq": 33, "id_num": "2-0033-3-018", "name": "经略台真武阁", "era": "明", "province": "广西", "city": "容县", "category": "ancient-buildings"},
    {"seq": 34, "id_num": "2-0034-3-019", "name": "瞿昙寺", "era": "明", "province": "青海", "city": "乐都县", "category": "ancient-buildings"},
    {"seq": 35, "id_num": "2-0035-3-020", "name": "北京城东南角楼", "era": "明", "province": "北京", "city": "北京市", "category": "ancient-buildings"},
    {"seq": 36, "id_num": "2-0036-3-021", "name": "都江堰", "era": "秦至清", "province": "四川", "city": "灌县", "category": "ancient-buildings"},
    {"seq": 37, "id_num": "2-0037-3-022", "name": "蓬莱水城及蓬莱阁", "era": "明", "province": "山东", "city": "蓬莱县", "category": "ancient-buildings"},
    {"seq": 38, "id_num": "2-0038-3-023", "name": "太和宫金殿", "era": "清", "province": "云南", "city": "昆明市", "category": "ancient-buildings"},
    {"seq": 39, "id_num": "2-0039-3-024", "name": "豫园", "era": "明至清", "province": "上海", "city": "上海市", "category": "ancient-buildings"},
    {"seq": 40, "id_num": "2-0040-3-025", "name": "恭王府及花园", "era": "清", "province": "北京", "city": "北京市", "category": "ancient-buildings"},
    {"seq": 41, "id_num": "2-0041-3-026", "name": "网师园", "era": "清", "province": "江苏", "city": "苏州市", "category": "ancient-buildings"},
    {"seq": 42, "id_num": "2-0042-3-027", "name": "程阳永济桥", "era": "民国", "province": "广西", "city": "三江县", "category": "ancient-buildings"},
    {"seq": 43, "id_num": "2-0043-3-028", "name": "拉卜楞寺", "era": "清", "province": "甘肃", "city": "夏河县", "category": "ancient-buildings"},
    # 石刻及其他 (44-45)
    {"seq": 44, "id_num": "2-0044-4-001", "name": "常德铁幢", "era": "宋", "province": "湖南", "city": "常德市", "category": "others"},
    {"seq": 45, "id_num": "2-0045-4-002", "name": "地藏寺经幢", "era": "大理", "province": "云南", "city": "昆明市", "category": "others"},
    # 古遗址 (46-55)
    {"seq": 46, "id_num": "2-0046-1-001", "name": "元谋猿人遗址", "era": "旧石器时代", "province": "云南", "city": "元谋县", "category": "archaeological-sites"},
    {"seq": 47, "id_num": "2-0047-1-002", "name": "蓝田猿人遗址", "era": "旧石器时代", "province": "陕西", "city": "蓝田县", "category": "archaeological-sites"},
    {"seq": 48, "id_num": "2-0048-1-003", "name": "大汶口遗址", "era": "新石器时代", "province": "山东", "city": "泰安县", "category": "archaeological-sites"},
    {"seq": 49, "id_num": "2-0049-1-004", "name": "河姆渡遗址", "era": "新石器时代", "province": "浙江", "city": "余姚县", "category": "archaeological-sites"},
    {"seq": 50, "id_num": "2-0050-1-005", "name": "周原遗址", "era": "西周", "province": "陕西", "city": "扶风县", "category": "archaeological-sites"},
    {"seq": 51, "id_num": "2-0051-1-006", "name": "铜绿山古铜矿遗址", "era": "周至汉", "province": "湖北", "city": "大冶县", "category": "archaeological-sites"},
    {"seq": 52, "id_num": "2-0052-1-007", "name": "丸都山故城", "era": "高句丽", "province": "吉林", "city": "集安县", "category": "archaeological-sites"},
    {"seq": 53, "id_num": "2-0053-1-008", "name": "湖田古瓷窑址", "era": "五代至明", "province": "江西", "city": "景德镇", "category": "archaeological-sites"},
    {"seq": 54, "id_num": "2-0054-1-009", "name": "金上京会宁府遗址", "era": "金", "province": "黑龙江", "city": "阿城县", "category": "archaeological-sites"},
    {"seq": 55, "id_num": "2-0055-1-010", "name": "明中都皇故城及皇陵石刻", "era": "明", "province": "安徽", "city": "凤阳县", "category": "archaeological-sites"},
    # 古墓葬 (56-62)
    {"seq": 56, "id_num": "2-0056-2-001", "name": "司马迁墓和祠", "era": "西汉至宋", "province": "陕西", "city": "韩城县", "category": "ancient-tombs"},
    {"seq": 57, "id_num": "2-0057-2-002", "name": "杨粲墓", "era": "宋", "province": "贵州", "city": "遵义市", "category": "ancient-tombs"},
    {"seq": 58, "id_num": "2-0058-2-003", "name": "宋陵", "era": "北宋", "province": "河南", "city": "巩县", "category": "ancient-tombs"},
    {"seq": 59, "id_num": "2-0059-2-004", "name": "李时珍墓", "era": "明", "province": "湖北", "city": "蕲春县", "category": "ancient-tombs"},
    {"seq": 60, "id_num": "2-0060-2-005", "name": "郑成功墓", "era": "清", "province": "福建", "city": "南安县", "category": "ancient-tombs"},
    {"seq": 61, "id_num": "2-0061-2-006", "name": "清昭陵", "era": "清", "province": "辽宁", "city": "沈阳市", "category": "ancient-tombs"},
    {"seq": 62, "id_num": "2-0062-2-007", "name": "成吉思汗陵", "era": "1954年迁建", "province": "内蒙古", "city": "伊金霍洛旗", "category": "ancient-tombs"},
]

def build_item(raw):
    code = PROVINCE_CODE[raw["province"]]
    return {
        "id": raw["id_num"],
        "name": raw["name"],
        "level": "national",
        "batch": 2,
        "category": raw["category"],
        "province": PROVINCE_FULL[code],
        "city": raw["city"],
        "district": "",
        "address": "",
        "era": raw["era"],
        "description": "",
        "historical_value": "",
        "sources": ["维基百科-第二批全国重点文物保护单位"],
        "last_updated": "2026-03-06",
        "data_quality": "basic",
        "contributors": ["iBo"]
    }

def main():
    by_province = {}
    for raw in BATCH2:
        code = PROVINCE_CODE[raw["province"]]
        by_province.setdefault(code, []).append(build_item(raw))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "national-level")
    os.makedirs(out_dir, exist_ok=True)

    total_new = 0
    for code, items in sorted(by_province.items()):
        path = os.path.join(out_dir, f"{code}.json")
        existing = {}
        if os.path.exists(path):
            with open(path) as f:
                for item in json.load(f):
                    existing[item["id"]] = item
        for item in items:
            if item["id"] not in existing:
                existing[item["id"]] = item
                total_new += 1
            else:
                if "batch" not in existing[item["id"]]:
                    existing[item["id"]]["batch"] = 2
        merged = sorted(existing.values(), key=lambda x: x["id"])
        with open(path, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
        prov_new = sum(1 for i in items if i["id"] not in {})
        print(f"  {PROVINCE_FULL[code]} ({code}.json): {len(merged)} items total")

    print(f"\n✅ 第二批 62 项录入完成 (新增 {total_new} 项)")

if __name__ == "__main__":
    main()
